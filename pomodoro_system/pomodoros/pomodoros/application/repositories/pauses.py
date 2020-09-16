from abc import abstractmethod, ABC

from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.value_objects import DateFrameId


class PausesRepository(ABC):
    @abstractmethod
    def get(self, pause_id: DateFrameId) -> Pause:
        pass

    @abstractmethod
    def save(self, pause: Pause) -> None:
        pass
