from abc import ABC, abstractmethod

from pomodoros.domain.entities import Task


class TasksRepository(ABC):
    @abstractmethod
    def get(self, task_id) -> Task:
        pass

    @abstractmethod
    def save(self, task: Task) -> None:
        pass
