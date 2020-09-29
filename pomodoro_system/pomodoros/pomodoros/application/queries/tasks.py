from abc import ABC, abstractmethod
from typing import List, Optional

from pomodoros.domain.entities import Task
from pomodoros.domain.value_objects import PomodoroId


class GetTasksByPomodoroId(ABC):
    @abstractmethod
    def query(self, pomodoro_id: PomodoroId) -> Optional[List[Task]]:
        pass
