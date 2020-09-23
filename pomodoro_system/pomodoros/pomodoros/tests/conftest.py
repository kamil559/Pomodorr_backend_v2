import pytest

from pomodoros.domain.entities import Task, Project
from pomodoros.domain.value_objects import TaskStatus
from pomodoros.tests.factories import TaskFactory, ProjectFactory


@pytest.fixture()
def task() -> Task:
    return TaskFactory()


@pytest.fixture()
def completed_task() -> Task:
    return TaskFactory(status=TaskStatus.COMPLETED)


@pytest.fixture()
def project() -> Project:
    return ProjectFactory()


@pytest.fixture()
def project_already_containing_task(task) -> Project:
    duplicated_task_name = TaskFactory(name=task.name)
    return ProjectFactory(tasks=[duplicated_task_name])
