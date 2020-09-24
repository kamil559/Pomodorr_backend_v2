import operator
from dataclasses import dataclass
from datetime import timedelta, datetime
from functools import reduce
from gettext import gettext as _
from typing import Optional, List, Union

from foundation.value_objects import DateFrameDefinition, UserDateFrameDefinition
from pomodoros.domain.entities import DateFrame, Task
from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.exceptions import CollidingPomodoroWasFound, PomodoroErrorMarginExceeded
from pomodoros.domain.value_objects import FrameType, AcceptablePomodoroErrorMargin, TaskId, PomodoroId


@dataclass
class Pomodoro(DateFrame):
    id: PomodoroId
    task_id: TaskId
    contained_pauses: Optional[List[Pause]]
    frame_type = FrameType.TYPE_POMODORO

    @staticmethod
    def _get_maximal_duration(date_frame_definition: Union[DateFrameDefinition, UserDateFrameDefinition]) -> timedelta:
        return date_frame_definition.pomodoro_length

    @staticmethod
    def _date_is_lower_than_start(date_frame: DateFrame, start_date: datetime) -> bool:
        return date_frame.start_date > start_date

    @staticmethod
    def _date_is_lower_than_end(date_frame: DateFrame, end_date: datetime) -> bool:
        return date_frame.end_date > end_date

    def _check_pomodoro_length(self, maximal_duration: timedelta, checked_end_date: datetime) -> None:
        pomodoro_duration = checked_end_date - self.start_date
        pauses_duration = reduce(operator.add,
                                 (pause.end_date - pause.end_date for pause in self.contained_pauses),
                                 timedelta(0))

        total_duration = pomodoro_duration - pauses_duration
        duration_difference = total_duration - maximal_duration

        if duration_difference > AcceptablePomodoroErrorMargin:
            raise PomodoroErrorMarginExceeded(_('pomodoros.domain.entities.pomodoro.pomodoro_error_margin_exceeded'))

    @staticmethod
    def _check_for_colliding_pomodoros(recent_pomodoros: Optional[List['Pomodoro']],
                                       start_date: datetime, end_date: Optional[datetime] = None):

        def check_if_finished(date_frame: DateFrame) -> bool:
            return all([date_frame.start_date, date_frame.start_date is not None,
                        date_frame.end_date, date_frame.end_date is not None])

        def check_if_overlaps(pomodoro: Pomodoro, checked_date: datetime) -> bool:
            return pomodoro.start_date > checked_date or pomodoro.end_date > checked_date

        def validate_against_unfinished_pomodoro() -> List[Pomodoro]:
            return list(
                filter(lambda pomodoro:
                       check_if_finished(pomodoro) and
                       check_if_overlaps(pomodoro, start_date),
                       recent_pomodoros)
            )

        def validate_against_finished_pomodoro() -> List[Pomodoro]:
            return list(
                filter(lambda pomodoro:
                       check_if_finished(pomodoro) and
                       (check_if_overlaps(pomodoro, start_date) or
                        check_if_overlaps(pomodoro, end_date)), recent_pomodoros))

        if end_date is None:
            colliding_date_frames = validate_against_unfinished_pomodoro()
        else:
            colliding_date_frames = validate_against_finished_pomodoro()

        if len(colliding_date_frames):
            raise CollidingPomodoroWasFound(_('pomodoros.domain.entities.pomodoro.colliding_pomodoro_was_found'))

    def begin(self, related_task: Task, recent_pomodoros: Optional[List['Pomodoro']], start_date: datetime) -> None:
        related_task.check_can_perform_actions()
        super(Pomodoro, self).run_begin_date_frame_validations(start_date)
        self._check_for_colliding_pomodoros(recent_pomodoros, start_date)

        self.start_date = start_date

    def finish(self, date_frame_definition: Union[DateFrameDefinition, UserDateFrameDefinition], related_task: Task,
               recent_pomodoros: Optional[List['Pomodoro']], end_date: datetime) -> None:
        related_task.check_can_perform_actions()
        super(Pomodoro, self).run_finish_date_frame_validations(end_date)
        maximal_duration = self._get_maximal_duration(date_frame_definition)
        self._check_pomodoro_length(maximal_duration, end_date)
        self._check_for_colliding_pomodoros(recent_pomodoros, self.start_date, end_date)

        self.end_date = end_date
