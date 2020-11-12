import os
from datetime import datetime

import factory
import pytest
import pytz
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from foundation.models import User
from foundation.tests.factories import ORMUserDateFrameDefinitionFactory, ORMUserFactory
from pomodoros.domain.value_objects import TaskStatus
from pomodoros_infrastructure import PomodoroModel, ProjectModel, TaskModel
from pomodoros_infrastructure.tests.factories import ORMPauseFactory, ORMPomodoroFactory, ORMTaskFactory
from pony.orm import db_session
from web_app.flask_app import create_app


@pytest.fixture(scope="package")
def app() -> Flask:
    return create_app()


@pytest.fixture()
def client(app) -> FlaskClient:
    app.config.update(
        DEBUG=bool(os.getenv("DEBUG", False)),
        TESTING=bool(os.getenv("TESTING", False)),
    )
    return app.test_client()


@pytest.fixture()
def project_owner_authorization_token(app: Flask, client: FlaskClient, project_owner: User) -> str:
    with app.test_request_context():
        access_token = create_access_token(project_owner)
    return f"Bearer {access_token}"


@pytest.fixture()
def random_project_owner_authorization_token(app: Flask, client: FlaskClient, random_project_owner: User) -> str:
    with app.test_request_context():
        access_token = create_access_token(random_project_owner)
    return f"Bearer {access_token}"


@pytest.fixture()
def started_orm_pomodoro(orm_task: TaskModel) -> PomodoroModel:
    with db_session:
        return ORMPomodoroFactory(task=orm_task.id, start_date=datetime.now(tz=pytz.UTC), end_date=None)


@pytest.fixture()
def paused_orm_pomodoro(orm_task: TaskModel) -> PomodoroModel:
    with db_session:
        started_orm_pomodoro = ORMPomodoroFactory(task=orm_task.id, end_date=None)
        pause = ORMPauseFactory(start_date=datetime.now(tz=pytz.UTC), end_date=None)
        pause.pomodoro = started_orm_pomodoro
        return started_orm_pomodoro


@pytest.fixture()
def orm_completed_task(orm_project: ProjectModel) -> TaskModel:
    with db_session():
        return ORMTaskFactory(project=orm_project.id, status=TaskStatus.COMPLETED.value)


@pytest.fixture()
def user_data() -> dict:
    return factory.build(dict, FACTORY_CLASS=ORMUserFactory)


@pytest.fixture()
def unconfirmed_user():
    with db_session:
        user = ORMUserFactory(date_frame_definition=None, confirmed_at=None, active=False)
        ORMUserDateFrameDefinitionFactory(user=user)
        return user
