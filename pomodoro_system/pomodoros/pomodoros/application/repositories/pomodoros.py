from abc import abstractmethod, ABC

from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.value_objects import DateFrameId


class PomodorosRepository(ABC):
    @abstractmethod
    def get(self, pomodoro_id: DateFrameId) -> Pomodoro:
        pass

    @abstractmethod
    def save(self, pomodoro: Pomodoro) -> None:
        pass
