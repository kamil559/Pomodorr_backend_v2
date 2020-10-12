from flask import Flask
from flask_injector import FlaskInjector
from pony.flask import Pony

from main import initialize_application
from web_app.configuration import PomodorosWebb


def create_app() -> Flask:
    flask_app = Flask(__name__)

    pomodoros_app_context = initialize_application()
    FlaskInjector(flask_app, modules=[PomodorosWebb()], injector=pomodoros_app_context.injector)
    Pony(flask_app)

    return flask_app
