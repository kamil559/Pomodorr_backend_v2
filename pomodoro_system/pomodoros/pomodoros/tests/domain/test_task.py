import pytest

from pomodoros.domain.exceptions import TaskNameNotAvailableInNewProject, NoActionAllowedOnCompletedTask


def test_pin_to_project_successfully(task, project):
    task.pin_to_new_project(new_project=project)

    assert task.project == project


def test_pin_to_project_containing_task_with_the_same_name_fails(task, project_already_containing_task):
    with pytest.raises(TaskNameNotAvailableInNewProject):
        task.pin_to_new_project(new_project=project_already_containing_task)


def test_pin_to_project_on_completed_task_fails(completed_task, project):
    with pytest.raises(NoActionAllowedOnCompletedTask):
        completed_task.pin_to_new_project(new_project=project)
