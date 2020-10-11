from typing import Type

from pony.orm import ObjectNotFound

from exceptions import NotFound
from pomodoros.application.repositories.pauses import PauseRepository
from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.value_objects import PauseId
from pomodoros_infrastructure.models.date_frame import Pause as PauseModel


class SQLPauseRepository(PauseRepository):
    @staticmethod
    def _to_entity(pause_model: Type[PauseModel]) -> Pause:
        return Pause(pause_model.id, pause_model.start_date, pause_model.end_date)

    def get(self, pause_id: PauseId) -> Pause:
        try:
            pause = PauseModel[pause_id]
        except ObjectNotFound:
            raise NotFound()
        else:
            return self._to_entity(pause)

    @staticmethod
    def _get_for_update(pause_id: PauseId) -> Type[PauseModel]:
        return PauseModel.get_for_update(pause_id)

    def save(self, pause: Pause) -> None:
        values_to_update = {
            'start_date': pause.start_date,
            'end_date': pause.end_date,
        }

        pause = self._get_for_update(pause.id)
        pause.set(**values_to_update)
