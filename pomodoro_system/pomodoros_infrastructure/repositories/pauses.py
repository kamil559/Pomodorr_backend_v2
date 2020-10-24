from typing import Type

from pony.orm import ObjectNotFound

from foundation.exceptions import NotFound
from foundation.utils import to_utc, with_tzinfo
from pomodoros.application.repositories.pauses import PauseRepository
from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.value_objects import PauseId
from pomodoros_infrastructure.models.date_frame import PauseModel


class SQLPauseRepository(PauseRepository):
    @staticmethod
    def _to_entity(pause_model: Type[PauseModel]) -> Pause:
        return Pause(pause_model.id, with_tzinfo(pause_model.start_date), with_tzinfo(pause_model.end_date))

    def get(self, pause_id: PauseId) -> Pause:
        try:
            pause = PauseModel[pause_id]
        except ObjectNotFound:
            raise NotFound()
        else:
            return self._to_entity(pause)

    @staticmethod
    def _get_for_update(pause_id: PauseId) -> Type[PauseModel]:
        return PauseModel.get_for_update(id=pause_id)

    def save(self, pause: Pause) -> None:
        values_to_update = {
            "start_date": to_utc(pause.start_date),
            "end_date": to_utc(pause.end_date),
        }

        pause = self._get_for_update(pause.id)
        pause.set(**values_to_update)
