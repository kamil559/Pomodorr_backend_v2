from typing import Type

import pytz
from pony.orm import ObjectNotFound

from foundation.exceptions import NotFound
from pomodoros.application.repositories.pauses import PauseRepository
from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.value_objects import PauseId
from pomodoros_infrastructure.models.date_frame import PauseModel


class SQLPauseRepository(PauseRepository):
    @staticmethod
    def _to_entity(pause_model: Type[PauseModel]) -> Pause:
        return Pause(pause_model.id, pause_model.start_date.astimezone(tz=pytz.UTC),
                     pause_model.end_date.astimezone(tz=pytz.UTC))

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
            'start_date': pause.start_date,
            'end_date': pause.end_date,
        }

        pause = self._get_for_update(pause.id)
        pause.set(**values_to_update)
