from datetime import datetime
from typing import List, Type

import pytz
from pomodoros import GetRecentPomodoros, TaskId
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros_infrastructure.models import PomodoroModel
from pomodoros_infrastructure.repositories import SQLPomodoroRepository


class SQLGetRecentPomodoros(GetRecentPomodoros):
    @staticmethod
    def _to_entity(orm_pomodoro: Type[PomodoroModel]) -> Pomodoro:
        return SQLPomodoroRepository.to_domain_entity(orm_pomodoro)

    @staticmethod
    def _is_finished(pomodoro_model: Type[PomodoroModel]) -> bool:
        return pomodoro_model.start_date and pomodoro_model.end_date

    @staticmethod
    def _is_from_today(pomodoro_model: Type[PomodoroModel], today_date: datetime.date) -> bool:
        return pomodoro_model.start_date.date() == today_date or pomodoro_model.end_date.date() == today_date

    def query(self, task_id: TaskId) -> List[Pomodoro]:
        today_date = datetime.now(tz=pytz.UTC).date()
        recent_orm_pomodoros = PomodoroModel.select(
            lambda pomodoro: pomodoro.task.id == task_id
            and self._is_finished(pomodoro)
            and self._is_from_today(pomodoro, today_date)
        )

        return list(map(lambda orm_pomodoro: self._to_entity(orm_pomodoro), recent_orm_pomodoros))
