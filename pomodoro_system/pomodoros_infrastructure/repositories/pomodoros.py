from typing import Type

from pony.orm import ObjectNotFound

from exceptions import NotFound
from pomodoros import PomodoroRepository, PomodoroId
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros_infrastructure.models import Pomodoro as PomodoroModel


class SQLPomodoroRepository(PomodoroRepository):

    @staticmethod
    def _to_entity(pomodoro_model: Type[PomodoroModel]) -> Pomodoro:
        return Pomodoro(pomodoro_model.id, pomodoro_model.task_id, pomodoro_model.start_date, pomodoro_model.end_date,
                        pomodoro_model.contained_pauses)

    def get(self, pomodoro_id: PomodoroId) -> Pomodoro:
        try:
            pomodoro = PomodoroModel[pomodoro_id]
        except ObjectNotFound:
            raise NotFound()
        else:
            return self._to_entity(pomodoro)

    @staticmethod
    def _get_for_update(pomodoro_id: PomodoroId) -> Type[PomodoroModel]:
        return PomodoroModel.get_for_update(pomodoro_id)

    def save(self, pomodoro: Pomodoro) -> None:
        values_to_update = {
            'task_id': pomodoro.task_id,
            'start_date': pomodoro.start_date,
            'end_date': pomodoro.end_date,
            'contained_pauses': pomodoro.contained_pauses
        }

        pomodoro = self._get_for_update(pomodoro.id)
        pomodoro.set(**values_to_update)
