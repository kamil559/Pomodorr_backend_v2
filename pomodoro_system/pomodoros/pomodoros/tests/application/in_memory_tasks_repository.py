from typing import List, Optional, Dict

from pomodoros.application.repositories.tasks import TasksRepository
from pomodoros.domain.entities import Task
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.value_objects import TaskId


class InMemoryTasksRepository(TasksRepository):
    def __init__(self, initial_data: Optional[List[Task]] = None):
        if initial_data is not None:
            self._rows = dict(map(lambda task: (task.id, task), initial_data))
        else:
            self._rows = {}

    def get(self, task_id: TaskId) -> Optional[Pomodoro]:
        return self._rows[task_id]

    def save(self, task: Task) -> None:
        self._rows[task.id] = task

    @property
    def rows(self) -> Optional[Dict[TaskId, Task]]:
        return self._rows
