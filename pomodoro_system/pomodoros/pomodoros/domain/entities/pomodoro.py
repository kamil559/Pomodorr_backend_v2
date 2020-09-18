import operator
from dataclasses import dataclass
from datetime import timedelta, datetime
from functools import reduce
from typing import Optional, List, Set

from pomodoros.domain.entities import DateFrame, Task
from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.exceptions import CollidingDateFrameFound, PomodoroErrorMarginExceeded
from pomodoros.domain.value_objects import FrameType, DateFrameId, AcceptablePomodoroErrorMargin
from user_config.domain.entities.user_config import UserConfig


@dataclass
class Pomodoro(DateFrame):
    task: Task
    frame_type = FrameType.TYPE_POMODORO
    contained_pauses: Optional[List[Pause]]

    @property
    def maximal_duration(self) -> timedelta:
        date_frame_owner = self.task.project.owner
        user_config = date_frame_owner.config
        return self._normalized_length(user_config=user_config)

    def _normalized_length(self, user_config: UserConfig):
        if self.task.pomodoro_length is not None:
            return self.task.pomodoro_length
        return user_config.pomodoro_length

    def begin(self, start_date: datetime) -> None:
        self.check_related_task_is_already_finished()
        super(Pomodoro, self).run_begin_date_frame_validations(start_date=start_date)
        self._check_for_colliding_pomodoros(start_date=start_date, end_date=None)

        self.start_date = start_date

    def finish(self, end_date: datetime) -> None:
        self.task.check_can_perform_actions()
        super(Pomodoro, self).run_finish_date_frame_validations(end_date=end_date)
        self._check_pomodoro_length(checked_end_date=end_date)
        self._check_for_colliding_pomodoros(start_date=self.start_date, end_date=end_date,
                                            excluded_date_frame_ids=self.id)

        self.end_date = end_date

    @staticmethod
    def _date_is_lower_than_start(date_frame: DateFrame, start_date: datetime) -> bool:
        return date_frame.start_date > start_date

    @staticmethod
    def _date_is_lower_than_end(date_frame: DateFrame, end_date: datetime) -> bool:
        return date_frame.end_date > end_date

    def _check_pomodoro_length(self, checked_end_date: datetime) -> None:
        pomodoro_duration = checked_end_date - self.start_date
        pauses_duration = reduce(operator.add,
                                 (pause.end_date - pause.end_date for pause in self.contained_pauses),
                                 timedelta(0))

        total_duration = pomodoro_duration - pauses_duration
        duration_difference = total_duration - self.maximal_duration

        if duration_difference > AcceptablePomodoroErrorMargin:
            raise PomodoroErrorMarginExceeded

    def _check_for_colliding_pomodoros(self, start_date: datetime,
                                       end_date: Optional[datetime] = None,
                                       excluded_date_frame_ids: Optional[Set[DateFrameId]] = None):

        def check_if_excluded(pomodoro_id: DateFrameId) -> bool:
            return pomodoro_id not in excluded_date_frame_ids

        def check_if_finished(date_frame: DateFrame) -> bool:
            return all([date_frame.start_date, date_frame.start_date is not None,
                        date_frame.end_date, date_frame.end_date is not None])

        def check_if_overlaps(date_frame: DateFrame, checked_date: datetime) -> bool:
            return date_frame.start_date > checked_date or date_frame.end_date > checked_date

        def validate_against_unfinished_pomodoro() -> List[Pomodoro]:
            return list(
                filter(lambda pomodoro:
                       check_if_excluded(pomodoro.id) and
                       check_if_finished(pomodoro) and
                       check_if_overlaps(pomodoro, start_date),
                       self.task.pomodoros)
            )

        def validate_against_finished_pomodoro() -> List[Pomodoro]:
            return list(
                filter(lambda pomodoro:
                       check_if_excluded(pomodoro.id) and
                       (check_if_overlaps(pomodoro, start_date) or
                        check_if_overlaps(pomodoro, end_date)), self.task.pomodoros))

        if end_date is None:
            colliding_date_frames = validate_against_unfinished_pomodoro()
        else:
            colliding_date_frames = validate_against_finished_pomodoro()

        if len(colliding_date_frames):
            raise CollidingDateFrameFound
