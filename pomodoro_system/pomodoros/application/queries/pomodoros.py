from abc import ABC, abstractmethod
from typing import List

from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.value_objects import TaskId


class GetRecentPomodoros(ABC):
    @abstractmethod
    def query(self, task_id: TaskId) -> List[Pomodoro]:
        pass
