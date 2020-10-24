from abc import ABC, abstractmethod

from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.value_objects import PomodoroId


class PomodoroRepository(ABC):
    @abstractmethod
    def get(self, pomodoro_id: PomodoroId) -> Pomodoro:
        pass

    @abstractmethod
    def save(self, pomodoro: Pomodoro, create: bool = False) -> None:
        pass
