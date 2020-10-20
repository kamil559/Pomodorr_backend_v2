import os

from flask import Flask
from flask.testing import FlaskClient

from flask_app import create_app
from pomodoros_infrastructure.tests.conftest import *


@pytest.fixture(scope='module')
def app() -> Flask:
    return create_app()


@pytest.fixture()
def client(app) -> FlaskClient:
    app.config.update(
        DEBUG=bool(os.getenv('DEBUG', False)),
        TESTING=bool(os.getenv('TESTING', False)),
        SECRET_KEY=os.getenv('SECRET_KEY')
    )
    return app.test_client()
