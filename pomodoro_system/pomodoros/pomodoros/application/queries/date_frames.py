from abc import ABC, abstractmethod
from dataclasses import dataclass

from pomodoros.domain.value_objects import DateFrameId, TaskId


@dataclass
class DateFrameDto:
    id: DateFrameId


class GetCurrentDateFrameForTask(ABC):
    @abstractmethod
    def query(self, task_id: TaskId) -> DateFrameDto:
        pass
