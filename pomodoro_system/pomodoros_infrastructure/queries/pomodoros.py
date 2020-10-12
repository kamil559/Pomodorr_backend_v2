from datetime import datetime
from typing import Optional, List, Type

import pytz

from pomodoros import GetRecentPomodoros, TaskId, PomodoroDto
from pomodoros_infrastructure.models import Pomodoro as PomodoroModel


class SQLGetRecentPomodoros(GetRecentPomodoros):
    @staticmethod
    def _to_dto(pomodoro_model: Type[PomodoroModel]) -> PomodoroDto:
        return PomodoroDto(pomodoro_model.id, pomodoro_model.task_id, pomodoro_model.start_date,
                           pomodoro_model.end_date)

    @staticmethod
    def _is_finished(pomodoro_model: Type[PomodoroModel]) -> bool:
        return pomodoro_model.start_date and pomodoro_model.end_date

    @staticmethod
    def _is_from_today(pomodoro_model: Type[PomodoroModel], today_date: datetime.date) -> bool:
        return pomodoro_model.start_date.date() == today_date or pomodoro_model.end_date.date() == today_date

    def query(self, task_id: TaskId) -> Optional[List[PomodoroDto]]:
        today_date = datetime.now(tz=pytz.UTC).date()
        recent_pomodoros = PomodoroModel.select(
            lambda pomodoro: pomodoro.task_id == task_id and
                             self._is_finished(pomodoro) and
                             self._is_from_today(pomodoro, today_date)
        )

        if recent_pomodoros:
            return list(map(lambda pomodoro: self._to_dto(pomodoro), recent_pomodoros))
