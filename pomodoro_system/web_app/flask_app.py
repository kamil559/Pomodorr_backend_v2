import os

from flask import Flask
from flask_injector import FlaskInjector
from pony.flask import Pony

from blueprints.pomodoros import pomodoros_blueprint
from main import initialize_application
from web_app.configuration import PomodorosWebb


def create_app() -> Flask:
    flask_app = Flask(__name__)
    flask_app.config.update(
        TESTING=bool(os.getenv('TESTING', False)),
        SECRET_KEY=os.getenv('SECRET_KEY')
    )

    flask_app.register_blueprint(pomodoros_blueprint)

    pomodoros_app_context = initialize_application()
    FlaskInjector(flask_app, modules=[PomodorosWebb()], injector=pomodoros_app_context.injector)
    Pony(flask_app)

    return flask_app
