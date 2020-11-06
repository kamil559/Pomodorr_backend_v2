from datetime import datetime, timedelta

import pytest
from foundation.models import User, db
from foundation.tests.factories import ORMUserDateFrameDefinitionFactory, ORMUserFactory
from pomodoros_infrastructure import ProjectModel, TaskModel
from pomodoros_infrastructure.tests.factories import ORMProjectFactory, ORMTaskFactory
from pony.orm import BindingError, db_session


@pytest.fixture(scope="class")
def setup_teardown_tables() -> None:
    try:
        db.bind(provider="sqlite", filename=":memory:", create_db=True)
    except BindingError:
        pass
    else:
        db.generate_mapping(create_tables=True)
        yield
        db.drop_all_tables(with_all_data=True)
        db.disconnect()
        db.provider = db.schema = None


@pytest.fixture()
def project_owner() -> User:
    with db_session:
        user = ORMUserFactory(date_frame_definition=None)
        ORMUserDateFrameDefinitionFactory(user=user)
        return user


@pytest.fixture()
def random_project_owner() -> User:
    with db_session:
        user = ORMUserFactory(date_frame_definition=None)
        ORMUserDateFrameDefinitionFactory(user=user)
        return user


@pytest.fixture()
def orm_project(project_owner: User) -> ProjectModel:
    with db_session:
        return ORMProjectFactory(owner_id=project_owner.id)


@pytest.fixture()
def orm_second_project(project_owner: User) -> ProjectModel:
    with db_session:
        return ORMProjectFactory(owner_id=project_owner.id)


@pytest.fixture()
def orm_task(orm_project: ProjectModel) -> TaskModel:
    with db_session:
        return ORMTaskFactory(project_id=orm_project.id)


@pytest.fixture()
def orm_task_for_yesterday():
    with db_session:
        return ORMTaskFactory(due_date=datetime.now() - timedelta(days=1))
