from pomodoros.domain.entities import Task
from pomodoros.domain.exceptions import SubTaskNotAvailableInTask


def check_sub_task_name_available_in_task(sub_task_name: str, task: Task) -> None:
    sub_task_in_task = list(filter(lambda sub_task: sub_task.name == sub_task_name, task.sub_tasks))

    if len(sub_task_in_task):
        raise SubTaskNotAvailableInTask
