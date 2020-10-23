import os

from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token

from flask_app import create_app
from pomodoros_infrastructure.tests.conftest import *


@pytest.fixture(scope='package')
def app() -> Flask:
    return create_app()


@pytest.fixture()
def client(app) -> FlaskClient:
    app.config.update(
        DEBUG=bool(os.getenv('DEBUG', False)),
        TESTING=bool(os.getenv('TESTING', False)),
        SECRET_KEY=os.getenv('SECRET_KEY'),
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY')
    )
    return app.test_client()


@pytest.fixture()
def project_owner_authorization_token(app: Flask, client: FlaskClient, project_owner: User) -> str:
    with app.app_context():
        return f'Bearer {create_access_token(identity=str(project_owner.id))}'


@pytest.fixture()
def random_project_owner_authorization_token(app: Flask, client: FlaskClient, random_project_owner: User) -> str:
    with app.app_context():
        return f'Bearer {create_access_token(identity=str(random_project_owner.id))}'


@pytest.fixture()
def started_orm_pomodoro(orm_task: TaskModel) -> PomodoroModel:
    with db_session:
        return ORMPomodoroFactory(task_id=orm_task.id, end_date=None)


@pytest.fixture()
def paused_orm_pomodoro(orm_task: TaskModel) -> PomodoroModel:
    with db_session:
        started_orm_pomodoro = ORMPomodoroFactory(task_id=orm_task.id, end_date=None)
        pause = ORMPauseFactory(start_date=datetime.now(tz=pytz.UTC),
                                end_date=None)
        pause.pomodoro = started_orm_pomodoro
        return started_orm_pomodoro
