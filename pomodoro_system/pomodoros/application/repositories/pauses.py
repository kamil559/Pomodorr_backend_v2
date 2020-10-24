from abc import ABC, abstractmethod

from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.value_objects import PauseId


class PauseRepository(ABC):
    @abstractmethod
    def get(self, pause_id: PauseId) -> Pause:
        pass

    @abstractmethod
    def save(self, pause: Pause) -> None:
        pass
