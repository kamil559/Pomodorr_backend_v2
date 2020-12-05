import http
import os

from flask import Flask, jsonify, request
from flask_apispec import FlaskApiSpec
from flask_babelex import Babel, Domain, refresh
from flask_injector import FlaskInjector
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_mail import Mail
from flask_security import Security
from foundation.exceptions import AlreadyExists, NotFound
from foundation.i18n import N_, setup_i18n
from foundation.models import User, db
from foundation.value_objects import UserId
from injector import Injector
from main import initialize_application
from pony.flask import Pony
from pony.orm import db_session

from .authentication.helpers import is_token_revoked
from .blueprints.auth import auth_blueprint
from .blueprints.pomodoros import pomodoros_blueprint
from .blueprints.projects import projects_blueprint
from .blueprints.tasks import tasks_blueprint
from .blueprints.users import users_blueprint
from .commands import user_cli
from .configuration import PomodorosWeb
from .docs_definitions.apispec import api_spec
from .docs_definitions.auth import auth_api_definitions
from .security import PonyORMUserDatastore
from .settings_loader import (
    FlaskBaseSettingsLoader,
    FlaskLocalSettingsLoader,
    FlaskProductionSettingsLoader,
    FlaskStagingSettingsLoader,
    FlaskTestingSettingsLoader,
)


def load_flask_app_settings(existing_settings: dict) -> dict:
    base_settings_loader = FlaskBaseSettingsLoader()
    base_settings_loader.setup()

    if existing_settings["testing"]:
        setup_strategy = FlaskTestingSettingsLoader()
    elif existing_settings["debug"]:
        setup_strategy = FlaskLocalSettingsLoader()
    elif existing_settings["staging"]:
        setup_strategy = FlaskStagingSettingsLoader()
    else:
        setup_strategy = FlaskProductionSettingsLoader()
    setup_strategy.setup()

    updated_settings = {**base_settings_loader.settings_mapping, **setup_strategy.settings_mapping}

    return updated_settings


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(projects_blueprint)
    app.register_blueprint(tasks_blueprint)
    app.register_blueprint(pomodoros_blueprint)
    app.register_blueprint(users_blueprint)


def register_doc(app: Flask) -> None:
    app.config["APISPEC_SPEC"] = api_spec

    api_spec.path(**auth_api_definitions["register"]).path(**auth_api_definitions["confirm"]).path(
        **auth_api_definitions["reset_password"]
    ).path(**auth_api_definitions["set_new_password"])

    spec = FlaskApiSpec(app)
    for blueprint_name, blueprint in app.blueprints.items():
        if not hasattr(blueprint, "view_functions"):
            continue

        for view, endpoint, injector_bindings in blueprint.view_functions:
            if injector_bindings:
                spec.register(
                    view, blueprint=blueprint_name, endpoint=endpoint, resource_class_kwargs=injector_bindings
                )
            else:
                spec.register(view, blueprint=blueprint_name, endpoint=endpoint)


@db_session
def add_default_roles(app: Flask) -> None:
    datastore = app.extensions["security"].datastore
    if datastore.find_role("user") is None:
        db.Role(name="user", description="Regular user role", users=[])
    if datastore.find_role("admin") is None:
        db.Role(name="admin", description="Administrator role", users=[])


def inject_dependencies(app: Flask, injector: Injector) -> None:
    FlaskInjector(app, modules=[PomodorosWeb()], injector=injector)


def add_flask_commands(flask_app: Flask) -> None:
    flask_app.cli.add_command(user_cli)


def create_app() -> Flask:
    flask_app = Flask(__name__)
    pomodoro_app_context = initialize_application()

    flask_app.config.update(
        DEBUG=pomodoro_app_context.settings["debug"],
        TESTING=pomodoro_app_context.settings["testing"],
        STAGING=pomodoro_app_context.settings["staging"],
        SECRET_KEY=os.getenv("SECRET_KEY"),
        DEFAULT_LANGUAGE="en",
        ALLOWED_LANGUAGES={"en", "pl"},
        SECURITY_I18N_DOMAIN="pomodoro_security",
        UPLOAD_PATH="pomodoro_system/web_app/media/",
        ALLOWED_EXTENSIONS=[".jpg", ".png"],
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
    )

    additional_settings = load_flask_app_settings(pomodoro_app_context.settings)
    flask_app.config.update(additional_settings["base_settings"])
    flask_app.config.update(additional_settings["security"])
    flask_app.config.update(additional_settings["mail"])

    register_blueprints(flask_app)
    register_doc(flask_app)  # Needs to be done after registering the blueprints

    inject_dependencies(flask_app, pomodoro_app_context.injector)  # Needs to be injected after the blueprints are set

    babel_domain = Domain(dirname="locale", domain="messages")
    babel = Babel(flask_app, default_locale="pl", default_domain=babel_domain)
    refresh()

    Pony(flask_app)

    user_data_store = PonyORMUserDatastore(db=db, user_model=db.User, role_model=db.Role)
    Security().init_app(app=flask_app, datastore=user_data_store)
    add_default_roles(flask_app)

    Mail().init_app(app=flask_app)

    jwt = JWTManager(app=flask_app)

    add_flask_commands(flask_app)

    def get_language() -> str:
        return (
            request.accept_languages.best_match(flask_app.config["ALLOWED_LANGUAGES"])
            or flask_app.config["DEFAULT_LANGUAGE"]
        )

    @jwt.user_claims_loader
    def user_claims_to_access_token(user: User) -> dict:
        return {"roles": [role.name for role in user.roles]}

    @jwt.user_identity_loader
    def user_identity_lookup(user: User) -> UserId:
        return getattr(user, "id")

    @jwt.token_in_blacklist_loader
    def check_if_token_revoked(decrypted_token) -> bool:
        return is_token_revoked(decrypted_token)

    @babel.localeselector
    def get_locale():
        language = get_language()
        return language

    @flask_app.before_request
    def before():
        if not flask_app.config.get("TESTING"):
            language = get_language()
            setup_i18n(language or flask_app.config["DEFAULT_LANGUAGE"])

    @flask_app.errorhandler(http.HTTPStatus.UNAUTHORIZED)
    def unauthorized_404_handler(_error):
        return (
            jsonify({"msg": str(N_("You may not access the requested resource unless you log in."))}),
            http.HTTPStatus.UNAUTHORIZED,
        )

    @flask_app.errorhandler(NoAuthorizationError)
    def unauthorized_handler(_error):
        return (
            jsonify({"msg": str(N_("You may not access the requested resource unless you log in."))}),
            http.HTTPStatus.UNAUTHORIZED,
        )

    @flask_app.errorhandler(http.HTTPStatus.FORBIDDEN)
    def forbidden_handler(error):
        return (
            jsonify({"msg": str(error or N_("You don't have the permission to perform the action."))}),
            http.HTTPStatus.FORBIDDEN,
        )

    @flask_app.errorhandler(http.HTTPStatus.NOT_FOUND)
    def not_found_handler(_error):
        return jsonify({"msg": str(N_("The requested URL was not found."))}), http.HTTPStatus.NOT_FOUND

    @flask_app.errorhandler(http.HTTPStatus.INTERNAL_SERVER_ERROR)
    def internal_server_error_handler(error):
        return (
            jsonify(
                {
                    "msg": str(
                        error
                        or N_(
                            "Something went wrong. "
                            "Should the issue remain for a longer period, please contact the administrator."
                        )
                    )
                }
            ),
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    @flask_app.errorhandler(NotFound)
    def repo_not_found_handler(error):
        return (
            jsonify({"msg": str(error or N_("The requested resource was not found."))}),
            http.HTTPStatus.NOT_FOUND,
        )

    @flask_app.errorhandler(AlreadyExists)
    def object_already_exists_handler(error):
        return (
            jsonify(error.messages),
            http.HTTPStatus.BAD_REQUEST,
        )

    @flask_app.errorhandler(http.HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
    def too_large(_error):
        return (
            jsonify({"msg": str(N_("The file is too large."))}),
            http.HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
        )

    return flask_app
