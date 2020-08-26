from pomodoros.domain.entities import Task, Project
from pomodoros.domain.exceptions import TaskNameNotAvailableInNewProject, TaskAlreadyCompleted, TaskAlreadyActive
from pomodoros.domain.value_objects import TaskStatus


def check_task_name_available_in_project(task_name: str, project: Project) -> None:
    task_in_new_project = list(
        filter(lambda task: task.status == TaskStatus.ACTIVE and task.name == task_name, project.tasks))

    if len(task_in_new_project):
        raise TaskNameNotAvailableInNewProject


def check_task_already_active(task: Task) -> None:
    if task.status == TaskStatus.ACTIVE:
        raise TaskAlreadyActive


def check_is_task_already_completed(task: Task) -> None:
    if task.status == TaskStatus.COMPLETED:
        raise TaskAlreadyCompleted
