from typing import List, Optional, Dict

from pomodoros.application.repositories.pomodoros import PomodoroRepository
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.value_objects import PomodoroId


class InMemoryPomodorosRepository(PomodoroRepository):
    def __init__(self, initial_data: Optional[List[Pomodoro]] = None):
        if initial_data is not None:
            self._rows = dict(map(lambda pomodoro: (pomodoro.id, pomodoro), initial_data))
        else:
            self._rows = {}

    def get(self, pomodoro_id: PomodoroId) -> Pomodoro:
        return self._rows[pomodoro_id]

    def save(self, pomodoro: Pomodoro) -> None:
        self._rows[pomodoro.id] = pomodoro

    @property
    def rows(self) -> Optional[Dict[PomodoroId, Pomodoro]]:
        return self._rows
