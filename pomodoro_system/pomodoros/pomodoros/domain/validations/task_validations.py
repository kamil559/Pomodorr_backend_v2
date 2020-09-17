from pomodoros.domain.entities import Task
from pomodoros.domain.exceptions import TaskAlreadyActive
from pomodoros.domain.value_objects import TaskStatus


def check_task_already_active(task: Task) -> None:
    if task.status == TaskStatus.ACTIVE:
        raise TaskAlreadyActive
