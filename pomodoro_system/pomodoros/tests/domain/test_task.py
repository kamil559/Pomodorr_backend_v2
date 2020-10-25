import pytest
from pomodoros.domain.exceptions import (
    NoActionAllowedOnCompletedTask,
    TaskAlreadyActive,
    TaskAlreadyCompleted,
    TaskNameNotAvailableInNewProject,
)
from pomodoros.domain.value_objects import TaskStatus
from pomodoros.tests.factories import TaskFactory


def test_task_returns_proper_next_due_date(task):
    expected_next_due_date = task.due_date + task.renewal_interval

    assert task.next_due_date == expected_next_due_date


def test_complete_task_successfully(task):
    task.complete()

    assert task.status == TaskStatus.COMPLETED


def test_complete_already_completed_task_fails(completed_task):
    with pytest.raises(TaskAlreadyCompleted):
        completed_task.complete()


def test_pin_to_project_successfully(task, project, project_tasks):
    new_project_tasks = project_tasks
    task.pin_to_new_project(new_project_id=project.id, new_project_tasks=new_project_tasks)

    assert task.project_id == project.id


def test_pin_to_project_containing_task_with_the_same_name_fails(task, new_project_with_tasks):
    new_project, new_project_tasks = new_project_with_tasks

    with pytest.raises(TaskNameNotAvailableInNewProject):
        task.pin_to_new_project(new_project_id=new_project.id, new_project_tasks=new_project_tasks)


def test_pin_to_project_on_completed_task_fails(completed_task, project, project_tasks):
    with pytest.raises(NoActionAllowedOnCompletedTask):
        completed_task.pin_to_new_project(new_project_id=project.id, new_project_tasks=project_tasks)


def test_reactivate_task_successfully(completed_task):
    completed_task.reactivate(project_tasks=[completed_task])

    assert completed_task.status == TaskStatus.ACTIVE


def test_reactivate_already_active_task_fails(task):
    with pytest.raises(TaskAlreadyActive):
        task.reactivate(project_tasks=[task])


def test_reactivate_task_of_project_containing_task_with_the_same_name_fails(
    completed_task,
):
    task_with_the_same_name = TaskFactory(project_id=completed_task.project_id, name=completed_task.name)

    with pytest.raises(TaskNameNotAvailableInNewProject):
        completed_task.reactivate(project_tasks=[task_with_the_same_name])
