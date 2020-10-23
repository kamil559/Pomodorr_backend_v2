from typing import Type

from pony.orm import ObjectNotFound

from foundation.exceptions import NotFound, AlreadyExists
from foundation.utils import with_tzinfo, to_utc
from pomodoros import PomodoroRepository, PomodoroId
from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros_infrastructure import PauseModel
from pomodoros_infrastructure.models import PomodoroModel


class SQLPomodoroRepository(PomodoroRepository):
    @staticmethod
    def _to_entity(pomodoro_model: Type[PomodoroModel]) -> Pomodoro:
        return Pomodoro(pomodoro_model.id, pomodoro_model.task_id,
                        with_tzinfo(pomodoro_model.start_date), with_tzinfo(pomodoro_model.end_date),
                        list(map(lambda pause: Pause(pause.id, with_tzinfo(pause.start_date),
                                                     with_tzinfo(pause.end_date)),
                                 pomodoro_model.contained_pauses)))

    def get(self, pomodoro_id: PomodoroId) -> Pomodoro:
        try:
            pomodoro = PomodoroModel[pomodoro_id]
        except ObjectNotFound:
            raise NotFound()
        else:
            return self._to_entity(pomodoro)

    @staticmethod
    def _get_orm_instance(pomodoro_id: PomodoroId) -> Type[PomodoroModel]:
        try:
            orm_pomodoro = PomodoroModel.get_for_update(id=pomodoro_id)
        except ObjectNotFound:
            raise NotFound()
        else:
            return orm_pomodoro

    @staticmethod
    def _persist_new_orm_entity(pomodoro: Pomodoro) -> None:
        if PomodoroModel.exists(id=pomodoro.id):
            raise AlreadyExists()
        else:
            orm_pomodoro = PomodoroModel(id=pomodoro.id, frame_type=pomodoro.frame_type.value, task_id=pomodoro.task_id,
                                         start_date=to_utc(pomodoro.start_date), end_date=to_utc(pomodoro.end_date))
            contained_pauses = [PauseModel(id=pause.id, frame_type=pause.frame_type.value,
                                           start_date=to_utc(pause.start_date), end_date=to_utc(pause.end_date),
                                           pomodoro=orm_pomodoro) for pause in pomodoro.contained_pauses]
            orm_pomodoro.set(contained_pauses=contained_pauses)

    def save(self, pomodoro: Pomodoro, create: bool = False) -> None:
        values_to_save = {
            'task_id': pomodoro.task_id,
            'start_date': to_utc(pomodoro.start_date),
            'end_date': to_utc(pomodoro.end_date)
        }

        if create:
            self._persist_new_orm_entity(pomodoro)
        else:
            orm_pomodoro = self._get_orm_instance(pomodoro.id)
            orm_pomodoro.set(**values_to_save)

            if pomodoro.new_pause:
                orm_pause = PauseModel(id=pomodoro.new_pause.id, frame_type=pomodoro.new_pause.frame_type.value,
                                       start_date=to_utc(pomodoro.new_pause.start_date),
                                       end_date=to_utc(pomodoro.new_pause.end_date),
                                       pomodoro=orm_pomodoro)
                orm_pomodoro.contained_pauses.add(orm_pause)

            if pomodoro.modified_pauses:
                for pause in pomodoro.modified_pauses:
                    PauseModel[pause.id].set(**{'start_date': pause.start_date, 'end_date': pause.end_date})
