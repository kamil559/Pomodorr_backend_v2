from datetime import datetime
from typing import List, Type

import pytz
from foundation.utils import with_tzinfo
from pomodoros import GetRecentPomodoros, TaskId
from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros_infrastructure.models import PomodoroModel


class SQLGetRecentPomodoros(GetRecentPomodoros):
    @staticmethod
    def _to_entity(pomodoro_model: Type[PomodoroModel]) -> Pomodoro:
        return Pomodoro(
            pomodoro_model.id,
            pomodoro_model.task_id,
            with_tzinfo(pomodoro_model.start_date),
            with_tzinfo(pomodoro_model.end_date),
            list(
                map(
                    lambda pause: Pause(
                        pause.id,
                        with_tzinfo(pause.start_date),
                        with_tzinfo(pause.end_date),
                    ),
                    pomodoro_model.contained_pauses,
                )
            ),
        )

    @staticmethod
    def _is_finished(pomodoro_model: Type[PomodoroModel]) -> bool:
        return pomodoro_model.start_date and pomodoro_model.end_date

    @staticmethod
    def _is_from_today(pomodoro_model: Type[PomodoroModel], today_date: datetime.date) -> bool:
        return pomodoro_model.start_date.date() == today_date or pomodoro_model.end_date.date() == today_date

    def query(self, task_id: TaskId) -> List[Pomodoro]:
        today_date = datetime.now(tz=pytz.UTC).date()
        recent_pomodoros = PomodoroModel.select(
            lambda pomodoro: pomodoro.task_id == task_id
            and self._is_finished(pomodoro)
            and self._is_from_today(pomodoro, today_date)
        )

        return list(map(lambda orm_pomodoro: self._to_entity(orm_pomodoro), recent_pomodoros))
