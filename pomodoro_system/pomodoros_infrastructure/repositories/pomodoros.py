from gettext import gettext as _
from typing import Optional, Type

from foundation.exceptions import AlreadyExists, NotFound
from foundation.utils import to_utc, with_tzinfo
from pomodoros import PomodoroId, PomodoroRepository
from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros_infrastructure import PauseModel
from pomodoros_infrastructure.models import PomodoroModel
from pony.orm import ObjectNotFound


class SQLPomodoroRepository(PomodoroRepository):
    @classmethod
    def to_domain_entity(cls, orm_pomodoro: Type[PomodoroModel]) -> Pomodoro:
        return Pomodoro(
            id=orm_pomodoro.id,
            task_id=orm_pomodoro.task.id,
            start_date=with_tzinfo(orm_pomodoro.start_date),
            end_date=with_tzinfo(orm_pomodoro.end_date),
            contained_pauses=list(
                map(
                    lambda pause_entity: Pause(
                        id=pause_entity.id,
                        start_date=with_tzinfo(pause_entity.start_date),
                        end_date=with_tzinfo(pause_entity.end_date),
                    ),
                    orm_pomodoro.contained_pauses,
                )
            ),
        )

    @staticmethod
    def _persist_new_orm_pomodoro(pomodoro_entity: Pomodoro) -> None:
        if PomodoroModel.exists(id=pomodoro_entity.id, start_date=pomodoro_entity.start_date):
            raise AlreadyExists({"start_date": [_("Pomodoro already exists.")]})
        else:
            orm_pomodoro = PomodoroModel(
                id=pomodoro_entity.id,
                frame_type=pomodoro_entity.frame_type.value,
                task=pomodoro_entity.task_id,
                start_date=to_utc(pomodoro_entity.start_date),
                end_date=to_utc(pomodoro_entity.end_date),
            )
            [
                PauseModel(
                    id=pause.id,
                    frame_type=pause.frame_type.value,
                    start_date=to_utc(pause.start_date),
                    end_date=to_utc(pause.end_date),
                    pomodoro=orm_pomodoro,
                )
                for pause in pomodoro_entity.contained_pauses
            ]

    @staticmethod
    def _get_for_update(pomodoro_id: PomodoroId) -> Optional[Type[PomodoroModel]]:
        return PomodoroModel.get_for_update(id=pomodoro_id)

    def _update_existing_orm_pomodoro(self, pomodoro_entity: Pomodoro) -> None:
        values_to_save = {
            "task": pomodoro_entity.task_id,
            "start_date": to_utc(pomodoro_entity.start_date),
            "end_date": to_utc(pomodoro_entity.end_date),
        }
        orm_pomodoro = self._get_for_update(pomodoro_entity.id)

        if orm_pomodoro is not None:
            orm_pomodoro.set(**values_to_save)

            if pomodoro_entity.new_pause:
                orm_pause = PauseModel(
                    id=pomodoro_entity.new_pause.id,
                    frame_type=pomodoro_entity.new_pause.frame_type.value,
                    start_date=to_utc(pomodoro_entity.new_pause.start_date),
                    end_date=to_utc(pomodoro_entity.new_pause.end_date),
                    pomodoro=orm_pomodoro,
                )
                orm_pomodoro.contained_pauses.add(orm_pause)

            if pomodoro_entity.modified_pauses:
                for pause in pomodoro_entity.modified_pauses:
                    PauseModel[pause.id].set(**{"start_date": pause.start_date, "end_date": pause.end_date})

    def get(self, pomodoro_id: PomodoroId) -> Pomodoro:
        try:
            orm_pomodoro = PomodoroModel[pomodoro_id]
        except ObjectNotFound:
            raise NotFound(_("Pomodoro does not exist."))
        else:
            return self.to_domain_entity(orm_pomodoro)

    def save(self, pomodoro: Pomodoro, create: bool = False) -> None:
        if create:
            self._persist_new_orm_pomodoro(pomodoro)
        else:
            self._update_existing_orm_pomodoro(pomodoro)
