import os
from datetime import datetime
from typing import Type

import pytest
import pytz
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token, create_refresh_token, get_jti
from flask_security import UserDatastore
from foundation.models import User
from pomodoros.domain.value_objects import TaskStatus
from pomodoros_infrastructure import PomodoroModel, ProjectModel, TaskModel
from pomodoros_infrastructure.tests.factories import ORMPauseFactory, ORMPomodoroFactory, ORMTaskFactory
from pony.orm import db_session
from web_app.authentication.helpers import add_token_to_database, revoke_all_tokens
from web_app.authentication.models.token import Token
from web_app.flask_app import create_app


@pytest.fixture(scope="package")
def app() -> Flask:
    return create_app()


@pytest.fixture()
def user_datastore(app: Flask) -> UserDatastore:
    return app.extensions["security"].datastore


@pytest.fixture()
def client(app) -> FlaskClient:
    app.config.update(
        DEBUG=bool(os.getenv("DEBUG", False)),
        TESTING=bool(os.getenv("TESTING", False)),
    )
    return app.test_client()


@pytest.fixture()
def banned_user_access_token(app: Flask, banned_user: User) -> Type[Token]:
    with db_session, app.test_request_context():
        access_token = create_access_token(banned_user)
        add_token_to_database(access_token)
        revoke_all_tokens(banned_user.id)
    return access_token


@pytest.fixture()
def banned_user_refresh_token(app: Flask, banned_user: User) -> Type[Token]:
    with db_session, app.test_request_context():
        refresh_token = create_refresh_token(banned_user)
        add_token_to_database(refresh_token)
        revoke_all_tokens(banned_user.id)
    return refresh_token


@pytest.fixture()
def project_owner_access_token(app: Flask, project_owner: User) -> Type[Token]:
    with db_session, app.test_request_context():
        access_token = create_access_token(project_owner)
        add_token_to_database(access_token)
    return access_token


@pytest.fixture()
def project_owner_revoked_token(app: Flask, project_owner_access_token) -> Type[Token]:
    with db_session, app.test_request_context():
        jti = get_jti(project_owner_access_token)
        return Token.select().filter(jti=jti).get()


@pytest.fixture()
def project_owner_authorization_token(app: Flask, project_owner: User) -> str:
    with db_session, app.test_request_context():
        access_token = create_access_token(project_owner)
        add_token_to_database(access_token)
    return f"Bearer {access_token}"


@pytest.fixture()
def random_project_owner_authorization_token(app: Flask, random_project_owner: User) -> str:
    with db_session, app.test_request_context():
        access_token = create_access_token(random_project_owner)
        add_token_to_database(access_token)
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
