from abc import abstractmethod, ABC

from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.value_objects import PomodoroId


class PomodorosRepository(ABC):
    @abstractmethod
    def get(self, pomodoro_id: PomodoroId) -> Pomodoro:
        pass

    @abstractmethod
    def save(self, pomodoro: Pomodoro) -> None:
        pass
