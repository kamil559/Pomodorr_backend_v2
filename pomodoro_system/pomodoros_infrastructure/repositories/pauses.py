from gettext import gettext as _
from typing import Optional, Type

from foundation.exceptions import AlreadyExists, NotFound
from foundation.utils import to_utc, with_tzinfo
from pomodoros.application.repositories.pauses import PauseRepository
from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.value_objects import PauseId
from pomodoros_infrastructure.models.date_frame import PauseModel
from pony.orm import ObjectNotFound


class SQLPauseRepository(PauseRepository):
    @classmethod
    def to_domain_entity(cls, orm_pause: Type[PauseModel]) -> Pause:
        return Pause(
            id=orm_pause.id,
            start_date=with_tzinfo(orm_pause.start_date),
            end_date=with_tzinfo(orm_pause.end_date),
        )

    @staticmethod
    def _persist_new_orm_pause(pause_entity: Pause) -> None:
        if PauseModel.exists(id=pause_entity.id):
            raise AlreadyExists(_("Pause already exists."))
        else:
            Pause(
                id=pause_entity.id,
                start_date=to_utc(pause_entity.start_date),
                end_date=to_utc(pause_entity.end_date),
            )

    @staticmethod
    def _get_for_update(pause_id: PauseId) -> Optional[Type[PauseModel]]:
        return PauseModel.get_for_update(id=pause_id)

    def _update_existing_orm_pause(self, pause_entity: Pause) -> None:
        values_to_update = {
            "start_date": to_utc(pause_entity.start_date),
            "end_date": to_utc(pause_entity.end_date),
        }
        orm_pause = self._get_for_update(pause_entity.id)

        if orm_pause is not None:
            orm_pause.set(**values_to_update)

    def get(self, pause_id: PauseId) -> Pause:
        try:
            orm_pause = PauseModel[pause_id]
        except ObjectNotFound:
            raise NotFound(_("Pause does not exist."))
        else:
            return self.to_domain_entity(orm_pause)

    def save(self, pause: Pause, create: bool = False) -> None:
        if create:
            self._persist_new_orm_pause(pause)
        else:
            self._update_existing_orm_pause(pause)
