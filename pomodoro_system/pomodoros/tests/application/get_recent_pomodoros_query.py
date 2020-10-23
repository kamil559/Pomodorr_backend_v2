from typing import Optional, List

from foundation.utils import with_tzinfo
from pomodoros.application.queries.pomodoros import GetRecentPomodoros
from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.value_objects import TaskId


class GetRecentPomodorosStub(GetRecentPomodoros):
    def __init__(self, return_collection: List[Pomodoro] = None):
        if return_collection is not None:
            self._rows = return_collection
        else:
            self._rows = []

    @staticmethod
    def _to_pomodoro_dto(pomodoro: Pomodoro) -> Pomodoro:
        return Pomodoro(pomodoro.id, pomodoro.task_id, with_tzinfo(pomodoro.start_date), with_tzinfo(pomodoro.end_date),
                        list(map(lambda pause: Pause(pause.id, with_tzinfo(pause.start_date),
                                                     with_tzinfo(pause.end_date)),
                                 pomodoro.contained_pauses)))

    def query(self, task_id: TaskId) -> Optional[List[Pomodoro]]:
        return list(map(lambda pomodoro: self._to_pomodoro_dto(pomodoro),
                        filter(lambda row: row.id == task_id, self._rows))) if self._rows else []
