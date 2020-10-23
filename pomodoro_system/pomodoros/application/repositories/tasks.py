from abc import ABC, abstractmethod

from pomodoros.domain.entities import Task
from pomodoros.domain.value_objects import TaskId


class TaskRepository(ABC):
    @abstractmethod
    def get(self, task_id: TaskId) -> Task:
        pass

    @abstractmethod
    def save(self, task: Task, create: bool = False) -> None:
        pass
