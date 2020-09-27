from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from pomodoros.domain.value_objects import TaskId, PomodoroId


@dataclass
class PomodoroDto:
    id: PomodoroId
    task_id: TaskId
    start_date: datetime
    end_date: datetime


class GetRecentPomodoros(ABC):
    @abstractmethod
    def query(self, task_id: TaskId) -> Optional[List[PomodoroDto]]:
        pass
