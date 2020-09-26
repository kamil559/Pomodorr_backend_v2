from datetime import timedelta, datetime
from typing import List, Tuple

import pytest

from foundation.value_objects import DateFrameDefinition
from pomodoros.domain.entities import Task, Project
from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.value_objects import TaskStatus
from pomodoros.tests.factories import TaskFactory, ProjectFactory, PomodoroFactory, DateFrameDefinitionFactory, \
    PauseFactory


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
def new_project_with_tasks(task: Task) -> Tuple[Project, List[Task]]:
    new_project = ProjectFactory()
    new_task = TaskFactory(project_id=new_project.id)
    duplicated_task_name = TaskFactory(name=task.name, project_id=new_project.id)

    return new_project, [new_task, duplicated_task_name]


@pytest.fixture()
def pomodoro(task: Task) -> Pomodoro:
    return PomodoroFactory(task_id=task.id)


@pytest.fixture()
def pomodoro_on_completed_task(completed_task: Task) -> Pomodoro:
    return PomodoroFactory(task_id=completed_task.id)


@pytest.fixture()
def started_pomodoro(task: Task) -> Pomodoro:
    now = datetime.now()
    return PomodoroFactory(start_date=now, task_id=task.id)


@pytest.fixture()
def finished_pomodoro(task: Task) -> Pomodoro:
    start_date = datetime.now()
    end_date = start_date + timedelta(minutes=25)
    return PomodoroFactory(task_id=task.id, start_date=start_date, end_date=end_date)


@pytest.fixture()
def pause() -> Pause:
    return PauseFactory()


@pytest.fixture()
def paused_pomodoro(pause: Pause, task: Task) -> Pomodoro:
    start_date = datetime.now()
    return PomodoroFactory(task_id=task.id, start_date=start_date, contained_pauses=[pause, ])


@pytest.fixture()
def overlapping_unfinished_pomodoros() -> List[Pomodoro]:
    now = datetime.now()
    first_overlapping_pomodoro = PomodoroFactory(start_date=now + timedelta(minutes=5))
    second_overlapping_pomodoro = PomodoroFactory(start_date=now + timedelta(minutes=10))
    return [first_overlapping_pomodoro, second_overlapping_pomodoro]


@pytest.fixture()
def finished_non_overlapping_pomodoros() -> List[Pomodoro]:
    now = datetime.now()
    first_finished_pomodoro = PomodoroFactory(start_date=now - timedelta(minutes=45),
                                              end_date=now - timedelta(minutes=30))
    second_finished_pomodoro = PomodoroFactory(start_date=now - timedelta(minutes=25),
                                               end_date=now - timedelta(minutes=5))
    return [first_finished_pomodoro, second_finished_pomodoro]


@pytest.fixture()
def overlapping_finished_pomodoros() -> List[Pomodoro]:
    now = datetime.now()
    first_overlapping_pomodoro = PomodoroFactory(start_date=now + timedelta(minutes=5),
                                                 end_date=now + timedelta(minutes=25))
    second_overlapping_pomodoro = PomodoroFactory(start_date=now + timedelta(minutes=30),
                                                  end_date=now + timedelta(minutes=55))
    return [first_overlapping_pomodoro, second_overlapping_pomodoro]


@pytest.fixture()
def date_frame_definition() -> DateFrameDefinition:
    return DateFrameDefinitionFactory()
