from typing import Optional, List

from pomodoros.application.queries.pomodoros import GetRecentPomodoros, PomodoroDto
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.value_objects import TaskId


class GetRecentPomodorosStub(GetRecentPomodoros):
    def __init__(self, return_collection: Optional[List[Pomodoro]] = None):
        if return_collection is not None:
            self._rows = return_collection
        else:
            self._rows = []

    @staticmethod
    def _to_pomodoro_dto(pomodoro: Pomodoro) -> PomodoroDto:
        return PomodoroDto(pomodoro.id, pomodoro.task_id, pomodoro.start_date, pomodoro.end_date)

    def query(self, task_id: TaskId) -> Optional[List[PomodoroDto]]:
        return list(map(lambda pomodoro: self._to_pomodoro_dto(pomodoro),
                        filter(lambda row: row.task_id == task_id, self._rows)))
