from typing import List
from unittest.mock import Mock

import pytest

from pomodoros.application.queries.pomodoros import GetRecentPomodoros
from pomodoros.application.repositories.pomodoros import PomodorosRepository
from pomodoros.application.repositories.tasks import TasksRepository
from pomodoros.application.use_cases.begin_pomodoro import (BeginPomodoro, BeginPomodoroOutputBoundary)
from pomodoros.domain.entities import Task, Project
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.tests.application.get_recent_pomodoros_query import GetRecentPomodorosStub
from pomodoros.tests.application.in_memory_pomodoros_repository import InMemoryPomodorosRepository
from pomodoros.tests.application.in_memory_tasks_repository import InMemoryTasksRepository
from pomodoros.tests.factories import PomodoroFactory, TaskFactory


@pytest.fixture()
def begin_pomodoro_output_boundary() -> Mock:
    return Mock(spec_set=BeginPomodoroOutputBoundary)


@pytest.fixture()
def recent_pomodoros_list(task: Task) -> List[Pomodoro]:
    pomodoros = [PomodoroFactory(task_id=task.id), PomodoroFactory(task_id=task.id), PomodoroFactory(task_id=task.id)]
    return pomodoros


@pytest.fixture()
def pomodoros_repository() -> PomodorosRepository:
    return InMemoryPomodorosRepository()


@pytest.fixture()
def tasks_repository() -> TasksRepository:
    return InMemoryTasksRepository()


@pytest.fixture()
def populated_tasks_repository(task: Task, project: Project) -> TasksRepository:
    another_tasks = [TaskFactory(project_id=task.project_id), TaskFactory(project_id=task.project_id)]
    return InMemoryTasksRepository(initial_data=[task] + another_tasks)


@pytest.fixture()
def recent_pomodoros_query() -> GetRecentPomodoros:
    return GetRecentPomodorosStub()


@pytest.fixture()
def populated_recent_pomodoros_query(recent_pomodoros_list: List[Pomodoro]):
    return GetRecentPomodorosStub(return_collection=recent_pomodoros_list)


@pytest.fixture()
def begin_pomodoro_use_case(begin_pomodoro_output_boundary: Mock, pomodoros_repository,
                            populated_tasks_repository, populated_recent_pomodoros_query) -> BeginPomodoro:
    return BeginPomodoro(output_boundary=begin_pomodoro_output_boundary, pomodoros_repository=pomodoros_repository,
                         tasks_repository=populated_tasks_repository,
                         recent_pomodoros_query=populated_recent_pomodoros_query)
