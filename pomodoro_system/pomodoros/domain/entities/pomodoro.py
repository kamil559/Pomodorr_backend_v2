import operator
import uuid
from datetime import datetime, timedelta
from functools import reduce
from typing import List, Optional, Union

from foundation.i18n import N_
from foundation.value_objects import DateFrameDefinition, UserDateFrameDefinition
from pomodoros.domain.entities import DateFrame, Task
from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.exceptions import (
    CollidingPomodoroWasFound,
    NoActionAllowedOnFinishedPomodoro,
    PomodoroErrorMarginExceeded,
)
from pomodoros.domain.value_objects import AcceptablePomodoroErrorMargin, FrameType, PomodoroId, TaskId


class Pomodoro(DateFrame):
    frame_type = FrameType.TYPE_POMODORO

    def __init__(
        self,
        id: PomodoroId,
        task_id: TaskId,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        contained_pauses: Optional[List[Pause]] = None,
    ) -> None:
        super().__init__(start_date=start_date, end_date=end_date)
        self.id = id
        self.task_id = task_id
        self.contained_pauses = (
            sorted(contained_pauses, key=lambda pause: pause.end_date) if contained_pauses is not None else []
        )
        self.modified_pauses: List[Pause] = []
        self.new_pause = None

    @property
    def current_pause(self) -> Optional[Pause]:
        ongoing_pauses = list(filter(lambda pause: not pause.is_finished, self.contained_pauses))
        if len(ongoing_pauses):
            return ongoing_pauses[-1]

    @staticmethod
    def _get_maximal_duration(date_frame_definition: Union[DateFrameDefinition, UserDateFrameDefinition]) -> timedelta:
        return date_frame_definition.pomodoro_length

    def _check_can_perform_actions(self) -> None:
        if self.is_finished:
            raise NoActionAllowedOnFinishedPomodoro(
                N_("pomodoros.domain.entities.pomodoro.no_action_allowed_on_finished_pomodoro")
            )

    def _check_pomodoro_length(self, maximal_duration: timedelta, checked_end_date: datetime) -> None:
        pomodoro_duration = checked_end_date - self.start_date
        pauses_duration = reduce(
            operator.add,
            (pause.end_date - pause.end_date for pause in self.contained_pauses),
            timedelta(0),
        )

        total_duration = pomodoro_duration - pauses_duration
        duration_difference = total_duration - maximal_duration

        if duration_difference > AcceptablePomodoroErrorMargin:
            raise PomodoroErrorMarginExceeded(N_("pomodoros.domain.entities.pomodoro.pomodoro_error_margin_exceeded"))

    @staticmethod
    def _check_for_colliding_pomodoros(
        recent_pomodoros: Optional[List["Pomodoro"]],
        start_date: datetime,
        end_date: Optional[datetime] = None,
    ):
        def check_if_finished(date_frame: DateFrame) -> bool:
            return all(
                [
                    date_frame.start_date,
                    date_frame.start_date is not None,
                    date_frame.end_date,
                    date_frame.end_date is not None,
                ]
            )

        def check_if_overlaps(pomodoro: Pomodoro, checked_date: datetime) -> bool:
            return pomodoro.start_date > checked_date or pomodoro.end_date > checked_date

        def validate_against_unfinished_pomodoro() -> List[Pomodoro]:
            return list(
                filter(
                    lambda pomodoro: check_if_finished(pomodoro) and check_if_overlaps(pomodoro, start_date),
                    recent_pomodoros,
                )
            )

        def validate_against_finished_pomodoro() -> List[Pomodoro]:
            return list(
                filter(
                    lambda pomodoro: check_if_finished(pomodoro)
                    and (check_if_overlaps(pomodoro, start_date) or check_if_overlaps(pomodoro, end_date)),
                    recent_pomodoros,
                )
            )

        if end_date is None:
            colliding_date_frames = validate_against_unfinished_pomodoro()
        else:
            colliding_date_frames = validate_against_finished_pomodoro()

        if len(colliding_date_frames):
            raise CollidingPomodoroWasFound(N_("pomodoros.domain.entities.pomodoro.colliding_pomodoro_was_found"))

    def begin(
        self,
        related_task: Task,
        recent_pomodoros: List["Pomodoro"],
        start_date: datetime,
    ) -> None:
        related_task.check_can_perform_actions()
        super(Pomodoro, self).run_begin_date_frame_validations(start_date)
        self._check_for_colliding_pomodoros(recent_pomodoros, start_date)

        self.start_date = start_date

    def finish(
        self,
        date_frame_definition: DateFrameDefinition,
        related_task: Task,
        recent_pomodoros: Optional[List["Pomodoro"]],
        end_date: datetime,
    ) -> None:
        related_task.check_can_perform_actions()
        super(Pomodoro, self).run_finish_date_frame_validations(end_date)
        maximal_duration = self._get_maximal_duration(date_frame_definition)
        self._check_pomodoro_length(maximal_duration, end_date)
        self._check_for_colliding_pomodoros(recent_pomodoros, self.start_date, end_date)

        self.end_date = end_date

    @staticmethod
    def _produce_new_pause_object(start_date: datetime) -> Pause:
        new_pause = Pause(id=uuid.uuid4(), start_date=start_date)
        new_pause.run_begin_date_frame_validations(start_date)
        return new_pause

    def pause(self, related_task: Task, start_date: datetime):
        related_task.check_can_perform_actions()
        self._check_can_perform_actions()

        if self.current_pause is None:
            self.new_pause = self._produce_new_pause_object(start_date)

    def resume(self, related_task: Task, end_date: datetime):
        related_task.check_can_perform_actions()
        self._check_can_perform_actions()
        pause_to_finish = self.current_pause
        if pause_to_finish is not None:
            pause_to_finish.run_finish_date_frame_validations(end_date)
            pause_to_finish.end_date = end_date
            self.modified_pauses.append(pause_to_finish)

    def __eq__(self, other) -> bool:
        return [
            type(self),
            self.task_id,
            self.frame_type,
            self.start_date,
            self.end_date,
            list(self.contained_pauses),
        ] == [
            type(other),
            other.id,
            other.frame_type,
            other.start_date,
            other.end_date,
            list(other.contained_pauses),
        ]
