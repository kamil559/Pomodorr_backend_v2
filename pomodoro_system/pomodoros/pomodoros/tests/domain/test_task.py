import pytest

from pomodoros.domain.exceptions import TaskNameNotAvailableInNewProject, NoActionAllowedOnCompletedTask


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
