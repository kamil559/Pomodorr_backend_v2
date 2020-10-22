import os
import uuid
from typing import Optional

from flask import Flask
from flask_injector import FlaskInjector
from flask_jwt_extended import JWTManager
from pony.flask import Pony

from blueprints.pomodoros import pomodoros_blueprint
from foundation.value_objects import UserId
from main import initialize_application
from web_app.configuration import PomodorosWeb


def create_app() -> Flask:
    flask_app = Flask(__name__)
    flask_app.config.update(
        TESTING=bool(os.getenv('TESTING', False)),
        SECRET_KEY=os.getenv('SECRET_KEY'),
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY')
    )

    jwt = JWTManager(flask_app)  # noqa

    flask_app.register_blueprint(pomodoros_blueprint)

    pomodoros_app_context = initialize_application()
    FlaskInjector(flask_app, modules=[PomodorosWeb()], injector=pomodoros_app_context.injector)
    Pony(flask_app)

    @jwt.user_loader_callback_loader
    def load_user_identity(identity: str) -> Optional[UserId]:
        try:
            user_id = uuid.UUID(identity)
        except ValueError:
            return
        else:
            return user_id

    return flask_app
