import os

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask
from flask_apispec import FlaskApiSpec
from flask_injector import FlaskInjector
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_security import Security
from foundation.models import User, db
from foundation.value_objects import UserId
from injector import Injector
from main import initialize_application
from pony.flask import Pony

from .authentication.endpoints import auth_blueprint
from .blueprints.pomodoros import pomodoros_blueprint
from .blueprints.tasks import tasks_blueprint
from .configuration import PomodorosWeb
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
    app.register_blueprint(pomodoros_blueprint)
    app.register_blueprint(tasks_blueprint)


def register_doc(app: Flask) -> None:
    api_spec = APISpec(
        title="Pomodoro App",
        version="0.1.0",
        openapi_version="2.0",
        info={
            "description": "The API documentation contains user-specific methods and authentication-related endpoints"
        },
        plugins=[MarshmallowPlugin()],
    )
    app.config["APISPEC_SPEC"] = api_spec

    api_spec.path(**auth_api_definitions["logout"]).path(**auth_api_definitions["register"]).path(
        **auth_api_definitions["confirm"]
    ).path(**auth_api_definitions["reset_password"]).path(**auth_api_definitions["set_new_password"])

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


def inject_dependencies(app: Flask, injector: Injector) -> None:
    FlaskInjector(app, modules=[PomodorosWeb()], injector=injector)


def create_app() -> Flask:
    flask_app = Flask(__name__)
    pomodoro_app_context = initialize_application()

    flask_app.config.update(
        DEBUG=pomodoro_app_context.settings["debug"],
        TESTING=pomodoro_app_context.settings["testing"],
        STAGING=pomodoro_app_context.settings["staging"],
        SECRET_KEY=os.getenv("SECRET_KEY"),
    )

    additional_settings = load_flask_app_settings(pomodoro_app_context.settings)
    flask_app.config.update(additional_settings["base_settings"])
    flask_app.config.update(additional_settings["security"])
    flask_app.config.update(additional_settings["mail"])

    register_blueprints(flask_app)
    register_doc(flask_app)  # Needs to be done after registering the blueprints

    inject_dependencies(flask_app, pomodoro_app_context.injector)  # Needs to be injected after the blueprints are set

    Pony(flask_app)

    user_data_store = PonyORMUserDatastore(db=db, user_model=db.User, role_model=db.Role)
    Security().init_app(app=flask_app, datastore=user_data_store)

    Mail().init_app(app=flask_app)

    jwt = JWTManager(app=flask_app)

    @jwt.user_claims_loader
    def user_claims_to_access_token(user: User) -> dict:
        return {"roles": [role.name for role in user.roles]}

    @jwt.user_identity_loader
    def user_identity_lookup(user: User) -> UserId:
        return getattr(user, "id")

    return flask_app
