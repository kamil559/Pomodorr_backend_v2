import os

import pytest
from flask import Flask
from flask.testing import FlaskClient
from pony.orm import db_session

from flask_app import create_app
from pomodoros_infrastructure import PomodoroModel
from pomodoros_infrastructure.tests.factories import ORMPomodoroFactory


@pytest.fixture(scope='package')
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


@pytest.fixture()
def started_orm_pomodoro() -> PomodoroModel:
    with db_session:
        return ORMPomodoroFactory(end_date=None)
