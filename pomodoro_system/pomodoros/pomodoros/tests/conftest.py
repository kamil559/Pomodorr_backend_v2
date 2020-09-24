from typing import List, Tuple

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
def project_tasks(project: Project) -> List[Task]:
    first_task = TaskFactory(project_id=project.id)
    second_task = TaskFactory(project_id=project.id)
    third_task = TaskFactory(project_id=project.id)

    return [first_task, second_task, third_task]


@pytest.fixture()
def new_project_with_tasks(task) -> Tuple[Project, List[Task]]:
    new_project = ProjectFactory()
    new_task = TaskFactory(project_id=new_project.id)
    duplicated_task_name = TaskFactory(name=task.name, project_id=new_project.id)

    return new_project, [new_task, duplicated_task_name]
