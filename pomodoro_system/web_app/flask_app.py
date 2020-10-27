import os

from flask import Flask
from flask_injector import FlaskInjector
from flask_mail import Mail
from flask_security import Security
from foundation.models import db
from main import initialize_application
from pony.flask import Pony

from .blueprints.pomodoros import pomodoros_blueprint
from .blueprints.tasks import tasks_blueprint
from .configuration import PomodorosWeb
from .security import PonyORMUserDatastore


def create_app() -> Flask:
    flask_app = Flask(__name__)
    pomodoro_app_context = initialize_application()

    flask_app.config.update(
        DEBUG=pomodoro_app_context.settings["debug"],
        TESTING=pomodoro_app_context.settings["testing"],
        SECRET_KEY=os.getenv("SECRET_KEY"),
        # Flask-jwt-extended configuration
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY"),
        # Flask-security configuration
        SECURITY_TOKEN_AUTHENTICATION_HEADER=os.getenv("SECURITY_TOKEN_AUTHENTICATION_HEADER"),
        SECURITY_REGISTERABLE=bool(int(os.getenv("SECURITY_REGISTERABLE"))),
        SECURITY_SEND_REGISTER_EMAIL=bool(int(os.getenv("SECURITY_SEND_REGISTER_EMAIL"))),
        SECURITY_CONFIRMABLE=bool(int(os.getenv("SECURITY_CONFIRMABLE"))),
        SECURITY_CHANGEABLE=bool(int(os.getenv("SECURITY_CHANGEABLE"))),
        SECURITY_RECOVERABLE=bool(int(os.getenv("SECURITY_RECOVERABLE"))),
        SECURITY_LOGIN_WITHOUT_CONFIRMATION=bool(int(os.getenv("SECURITY_LOGIN_WITHOUT_CONFIRMATION"))),
        SECURITY_CONFIRM_EMAIL_WITHIN=os.getenv("SECURITY_CONFIRM_EMAIL_WITHIN"),
        SECURITY_RESET_PASSWORD_WITHIN=os.getenv("SECURITY_RESET_PASSWORD_WITHIN"),
        SECURITY_EMAIL_SUBJECT_REGISTER=os.getenv("SECURITY_EMAIL_SUBJECT_REGISTER"),
        SECURITY_CONFIRM_SALT=os.getenv("SECURITY_CONFIRM_SALT"),
        SECURITY_RESET_SALT=os.getenv("SECURITY_RESET_SALT"),
        SECURITY_LOGIN_SALT=os.getenv("SECURITY_LOGIN_SALT"),
        SECURITY_PASSWORD_SALT=os.getenv("SECURITY_PASSWORD_SALT"),
        SECURITY_EMAIL_SENDER=os.getenv("SECURITY_EMAIL_SENDER"),
        WTF_CSRF_ENABLED=bool(int(os.getenv("WTF_CSRF_ENABLED"))),
        SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS=True,
        # Flask-mail configurations
        MAIL_SERVER=os.getenv("MAIL_SERVER"),
        MAIL_PORT=os.getenv("MAIL_PORT"),
        MAIL_USE_TLS=bool(int(os.getenv("MAIL_USE_TLS"))),
        MAIL_USE_SSL=bool(int(os.getenv("MAIL_USE_SSL"))),
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER"),
        MAIL_MAX_EMAILS=os.getenv("MAIL_MAX_EMAILS"),
        MAIL_ASCII_ATTACHMENTS=bool(int(os.getenv("MAIL_ASCII_ATTACHMENTS"))),
    )

    flask_app.register_blueprint(pomodoros_blueprint)
    flask_app.register_blueprint(tasks_blueprint)

    FlaskInjector(flask_app, modules=[PomodorosWeb()], injector=pomodoro_app_context.injector)

    Pony(flask_app)

    user_data_store = PonyORMUserDatastore(db=db, user_model=db.User, role_model=db.Role)
    Security().init_app(app=flask_app, datastore=user_data_store)

    Mail().init_app(app=flask_app)

    return flask_app
