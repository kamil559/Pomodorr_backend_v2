from datetime import datetime, timedelta

import pytest
from foundation.models import User, db
from foundation.tests.factories import ORMUserDateFrameDefinitionFactory, ORMUserFactory
from pomodoros.domain.value_objects import TaskStatus
from pomodoros.tests.factories import ProjectFactory, TaskFactory
from pomodoros_infrastructure import ProjectModel, TaskModel
from pomodoros_infrastructure.tests.factories import ORMProjectFactory, ORMTaskFactory
from pony.orm import BindingError, db_session
from web_app.serializers.projects import ProjectRestSchema
from web_app.serializers.tasks import TaskRestSchema


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
def project_data(project_owner: User) -> dict:
    raw_data = ProjectFactory(owner_id=project_owner.id)
    return ProjectRestSchema(many=False).dump(raw_data)


@pytest.fixture()
def orm_second_project(project_owner: User) -> ProjectModel:
    with db_session:
        return ORMProjectFactory(owner_id=project_owner.id)


@pytest.fixture()
def orm_random_project() -> ProjectModel:
    with db_session:
        return ORMProjectFactory()


@pytest.fixture()
def orm_task(orm_project: ProjectModel) -> TaskModel:
    with db_session:
        return ORMTaskFactory(project=orm_project.id)


@pytest.fixture()
def orm_second_task(orm_task: TaskModel, orm_project: ProjectModel) -> TaskModel:
    with db_session:
        return ORMTaskFactory(project=orm_project.id, due_date=orm_task.due_date)


@pytest.fixture()
def completed_orm_task(orm_project: ProjectModel, orm_task: TaskModel) -> TaskModel:
    with db_session:
        return ORMTaskFactory(project=orm_project.id, status=TaskStatus.COMPLETED.value)


@pytest.fixture()
def task_data(orm_project: ProjectModel) -> dict:
    raw_data = TaskFactory(project_id=orm_project.id)
    return TaskRestSchema(many=False).dump(raw_data)


@pytest.fixture()
def orm_task_for_second_project(orm_second_project: ProjectModel) -> TaskModel:
    with db_session:
        return ORMTaskFactory(project=orm_second_project.id)


@pytest.fixture()
def orm_task_for_tomorrow(orm_task: TaskModel, orm_project: ProjectModel) -> TaskModel:
    with db_session:
        return ORMTaskFactory(project=orm_project.id, due_date=orm_task.due_date + timedelta(days=1))


@pytest.fixture()
def upcoming_orm_task(orm_task: TaskModel, orm_project: ProjectModel) -> TaskModel:
    with db_session:
        return ORMTaskFactory(project=orm_project.id, due_date=orm_task.due_date + timedelta(days=20))


@pytest.fixture()
def orm_random_task() -> TaskModel:
    with db_session:
        return ORMTaskFactory()


@pytest.fixture()
def orm_task_for_yesterday(orm_project: ProjectModel):
    with db_session:
        return ORMTaskFactory(project=orm_project.id, due_date=datetime.now() - timedelta(days=1))
