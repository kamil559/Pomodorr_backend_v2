from typing import List
from unittest.mock import Mock

import pytest

from foundation.application.repositories.user import UsersRepository
from foundation.domain.entities.user import AbstractUser
from foundation.domain.tests.factories import UserFactory
from pomodoros.application.queries.pomodoros import GetRecentPomodoros
from pomodoros.application.repositories.pomodoros import PomodorosRepository
from pomodoros.application.repositories.tasks import TasksRepository
from pomodoros.application.use_cases.begin_pomodoro import (BeginPomodoro, BeginPomodoroOutputBoundary)
from pomodoros.application.use_cases.complete_task import CompleteTaskOutputBoundary, CompleteTask
from pomodoros.application.use_cases.finish_pomodoro import FinishPomodoroOutputBoundary, FinishPomodoro
from pomodoros.domain.entities import Task, Project
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.tests.application.get_recent_pomodoros_query import GetRecentPomodorosStub
from pomodoros.tests.application.in_memory_pomodoros_repository import InMemoryPomodorosRepository
from pomodoros.tests.application.in_memory_tasks_repository import InMemoryTasksRepository
from pomodoros.tests.factories import PomodoroFactory, TaskFactory


@pytest.fixture()
def user() -> AbstractUser:
    return UserFactory()


@pytest.fixture()
def begin_pomodoro_output_boundary() -> Mock:
    return Mock(spec_set=BeginPomodoroOutputBoundary)


@pytest.fixture()
def pomodoros_repository() -> PomodorosRepository:
    return InMemoryPomodorosRepository()


@pytest.fixture()
def populated_pomodoros_repository(started_pomodoro: Pomodoro) -> PomodorosRepository:
    other_pomodoros = [PomodoroFactory(task_id=started_pomodoro.task_id),
                       PomodoroFactory(task_id=started_pomodoro.task_id)]
    return InMemoryPomodorosRepository(initial_data=[started_pomodoro] + other_pomodoros)


@pytest.fixture()
def tasks_repository() -> TasksRepository:
    return InMemoryTasksRepository()


@pytest.fixture()
def populated_tasks_repository(one_time_task: Task, task: Task, project: Project) -> TasksRepository:
    other_tasks = [TaskFactory(project_id=task.project_id), TaskFactory(project_id=task.project_id)]
    return InMemoryTasksRepository(initial_data=[one_time_task, task] + other_tasks)


@pytest.fixture()
def recent_pomodoros_query() -> GetRecentPomodoros:
    return GetRecentPomodorosStub()


@pytest.fixture()
def recent_pomodoros_list(task: Task) -> List[Pomodoro]:
    pomodoros = [PomodoroFactory(task_id=task.id), PomodoroFactory(task_id=task.id), PomodoroFactory(task_id=task.id)]
    return pomodoros


@pytest.fixture()
def populated_recent_pomodoros_query(recent_pomodoros_list: List[Pomodoro]) -> GetRecentPomodoros:
    return GetRecentPomodorosStub(return_collection=recent_pomodoros_list)


@pytest.fixture()
def begin_pomodoro_use_case(begin_pomodoro_output_boundary, pomodoros_repository, populated_tasks_repository,
                            populated_recent_pomodoros_query) -> BeginPomodoro:
    return BeginPomodoro(output_boundary=begin_pomodoro_output_boundary, pomodoros_repository=pomodoros_repository,
                         tasks_repository=populated_tasks_repository,
                         recent_pomodoros_query=populated_recent_pomodoros_query)


@pytest.fixture()
def users_repository(user: AbstractUser) -> Mock:
    return Mock(spec_set=UsersRepository, get=Mock(return_value=user))


@pytest.fixture()
def finish_pomodoro_output_boundary() -> Mock:
    return Mock(spec_set=FinishPomodoroOutputBoundary)


@pytest.fixture()
def finish_pomodoro_use_case(finish_pomodoro_output_boundary, populated_pomodoros_repository,
                             populated_tasks_repository, users_repository,
                             populated_recent_pomodoros_query) -> FinishPomodoro:
    return FinishPomodoro(output_boundary=finish_pomodoro_output_boundary,
                          pomodoros_repository=populated_pomodoros_repository,
                          tasks_repository=populated_tasks_repository, users_repository=users_repository,
                          recent_pomodoros_query=populated_recent_pomodoros_query)


@pytest.fixture()
def complete_task_output_boundary() -> Mock:
    return Mock(spec_set=CompleteTaskOutputBoundary)


@pytest.fixture()
def complete_task_use_case(complete_task_output_boundary, populated_tasks_repository) -> CompleteTask:
    return CompleteTask(output_boundary=complete_task_output_boundary, tasks_repository=populated_tasks_repository)
