from typing import List
from unittest.mock import Mock

import pytest

from foundation.application.repositories.user import UserRepository
from foundation.tests.factories import UserFactory
from interfaces import AbstractUser
from pomodoros.application.queries.pomodoros import GetRecentPomodoros
from pomodoros.application.queries.tasks import GetTasksByProjectId
from pomodoros.application.repositories.pomodoros import PomodoroRepository
from pomodoros.application.repositories.tasks import TaskRepository
from pomodoros.application.use_cases.begin_pomodoro import BeginPomodoro, BeginPomodoroOutputBoundary
from pomodoros.application.use_cases.complete_task import CompleteTaskOutputBoundary, CompleteTask
from pomodoros.application.use_cases.finish_pomodoro import FinishPomodoroOutputBoundary, FinishPomodoro
from pomodoros.application.use_cases.pause_pomodoro import PausePomodoro, PausePomodoroOutputBoundary
from pomodoros.application.use_cases.pin_task_to_project import PinTaskToProjectOutputBoundary, PinTaskToProject
from pomodoros.application.use_cases.reactivate_task import ReactivateTaskOutputBoundary, ReactivateTask
from pomodoros.application.use_cases.resume_pomodoro import ResumePomodoroOutputBoundary, ResumePomodoro
from pomodoros.domain.entities import Task
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.tests.application.get_recent_pomodoros_query import GetRecentPomodorosStub
from pomodoros.tests.application.get_tasks_by_pomodoro_id_query import GetTasksByProjectIdStub
from pomodoros.tests.application.in_memory_pomodoros_repository import InMemoryPomodorosRepository
from pomodoros.tests.application.in_memory_task_repository import InMemoryTaskRepository
from pomodoros.tests.factories import PomodoroFactory


@pytest.fixture()
def user() -> AbstractUser:
    return UserFactory()


@pytest.fixture()
def begin_pomodoro_output_boundary() -> Mock:
    return Mock(spec_set=BeginPomodoroOutputBoundary)


@pytest.fixture()
def pomodoros_repository() -> PomodoroRepository:
    return InMemoryPomodorosRepository()


@pytest.fixture()
def populated_pomodoros_repository(started_pomodoro: Pomodoro, paused_pomodoro: Pomodoro) -> PomodoroRepository:
    other_pomodoros = [
        PomodoroFactory(task_id=started_pomodoro.task_id),
        PomodoroFactory(task_id=started_pomodoro.task_id),
    ]
    return InMemoryPomodorosRepository(initial_data=[started_pomodoro, paused_pomodoro] + other_pomodoros)


@pytest.fixture()
def tasks_repository() -> TaskRepository:
    return InMemoryTaskRepository()


@pytest.fixture()
def populated_tasks_repository(one_time_task: Task, task: Task, completed_task: Task) -> TaskRepository:
    return InMemoryTaskRepository(initial_data=[one_time_task, task, completed_task])


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
def begin_pomodoro_use_case(
        begin_pomodoro_output_boundary, pomodoros_repository, populated_tasks_repository,
        populated_recent_pomodoros_query
) -> BeginPomodoro:
    return BeginPomodoro(
        output_boundary=begin_pomodoro_output_boundary,
        pomodoros_repository=pomodoros_repository,
        tasks_repository=populated_tasks_repository,
        recent_pomodoros_query=populated_recent_pomodoros_query,
    )


@pytest.fixture()
def users_repository(user: AbstractUser) -> Mock:
    return Mock(spec_set=UserRepository, get=Mock(return_value=user))


@pytest.fixture()
def finish_pomodoro_output_boundary() -> Mock:
    return Mock(spec_set=FinishPomodoroOutputBoundary)


@pytest.fixture()
def finish_pomodoro_use_case(
        finish_pomodoro_output_boundary,
        populated_pomodoros_repository,
        populated_tasks_repository,
        users_repository,
        populated_recent_pomodoros_query,
) -> FinishPomodoro:
    return FinishPomodoro(
        output_boundary=finish_pomodoro_output_boundary,
        pomodoro_repository=populated_pomodoros_repository,
        task_repository=populated_tasks_repository,
        user_repository=users_repository,
        recent_pomodoros_query=populated_recent_pomodoros_query,
    )


@pytest.fixture()
def complete_task_output_boundary() -> Mock:
    return Mock(spec_set=CompleteTaskOutputBoundary)


@pytest.fixture()
def complete_task_use_case(complete_task_output_boundary, populated_tasks_repository) -> CompleteTask:
    return CompleteTask(output_boundary=complete_task_output_boundary, task_repository=populated_tasks_repository)


@pytest.fixture()
def pause_pomodoro_output_boundary() -> Mock:
    return Mock(spec_set=PausePomodoroOutputBoundary)


@pytest.fixture()
def pause_pomodoro_use_case(
        pause_pomodoro_output_boundary, populated_pomodoros_repository, populated_tasks_repository
) -> PausePomodoro:
    return PausePomodoro(
        output_boundary=pause_pomodoro_output_boundary,
        pomodoros_repository=populated_pomodoros_repository,
        tasks_repository=populated_tasks_repository,
    )


@pytest.fixture()
def resume_pomodoro_output_boundary() -> Mock:
    return Mock(spec_set=ResumePomodoroOutputBoundary)


@pytest.fixture()
def resume_pomodoro_use_case(
        resume_pomodoro_output_boundary, populated_pomodoros_repository, populated_tasks_repository
) -> ResumePomodoro:
    return ResumePomodoro(
        output_boundary=resume_pomodoro_output_boundary,
        pomodoros_repository=populated_pomodoros_repository,
        tasks_repository=populated_tasks_repository,
    )


@pytest.fixture()
def populated_tasks_by_project_id_query(populated_tasks_repository: InMemoryTaskRepository) -> GetTasksByProjectId:
    return GetTasksByProjectIdStub(return_collection=list(populated_tasks_repository.rows.values()))


@pytest.fixture()
def pin_task_to_project_output_boundary() -> Mock:
    return Mock(spec_set=PinTaskToProjectOutputBoundary)


@pytest.fixture()
def pin_task_to_project_use_case(
        pin_task_to_project_output_boundary, populated_tasks_repository, populated_tasks_by_project_id_query
) -> PinTaskToProject:
    return PinTaskToProject(
        output_boundary=pin_task_to_project_output_boundary,
        tasks_repository=populated_tasks_repository,
        get_tasks_by_project_id_query=populated_tasks_by_project_id_query,
    )


@pytest.fixture()
def reactivate_task_output_boundary() -> Mock:
    return Mock(ReactivateTaskOutputBoundary)


@pytest.fixture()
def reactivate_task_use_case(
        reactivate_task_output_boundary, populated_tasks_repository, populated_tasks_by_project_id_query
) -> ReactivateTask:
    return ReactivateTask(
        output_boundary=reactivate_task_output_boundary,
        tasks_repository=populated_tasks_repository,
        get_tasks_by_pomodoro_id_query=populated_tasks_by_project_id_query,
    )
