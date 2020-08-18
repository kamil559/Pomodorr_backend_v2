from pomodoros.domain.entities import Task, Project
from pomodoros.domain.exceptions import TaskNameNotAvailableInNewProject, TaskAlreadyCompleted
from pomodoros.domain.value_objects import TaskStatus


def check_is_task_name_available_in_project(task_name: str, project: Project) -> None:
    task_in_new_project = list(filter(lambda task: task.name.lower() == task_name, project.tasks))

    if len(task_in_new_project):
        raise TaskNameNotAvailableInNewProject


def check_is_task_already_completed(task: Task) -> None:
    if task.status == TaskStatus.COMPLETED:
        raise TaskAlreadyCompleted
