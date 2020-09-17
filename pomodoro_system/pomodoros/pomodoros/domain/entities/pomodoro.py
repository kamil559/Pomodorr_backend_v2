from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import Optional, List, Set

from pomodoros.domain.entities import DateFrame, Task
from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.exceptions import CollidingDateFrameFound
from pomodoros.domain.value_objects import FrameType, DateFrameId
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
        super(Pomodoro, self).run_begin_date_frame_validations(start_date=start_date)

        self.start_date = start_date

    def finish(self, end_date: datetime) -> None:
        pass

    @staticmethod
    def _date_is_lower_than_start(date_frame: DateFrame, start_date: datetime) -> bool:
        return date_frame.start_date > start_date

    @staticmethod
    def _date_is_lower_than_end(date_frame: DateFrame, end_date: datetime) -> bool:
        return date_frame.end_date > end_date

    @staticmethod
    def _check_if_excluded(pomodoro_id: DateFrameId, excluded_date_frame_ids: Set[DateFrameId]) -> bool:
        return pomodoro_id not in excluded_date_frame_ids

    @staticmethod
    def _check_if_finished(date_frame: DateFrame) -> bool:
        return all([date_frame.start_date, date_frame.start_date is not None,
                    date_frame.end_date, date_frame.end_date is not None])

    @staticmethod
    def _check_if_overlaps(date_frame: DateFrame, checked_date: datetime) -> bool:
        return date_frame.start_date > checked_date or date_frame.end_date > checked_date

    @classmethod
    def check_for_colliding_pomodoros(cls, task: Task, start_date: datetime,
                                      end_date: Optional[datetime] = None,
                                      excluded_date_frame_ids: Optional[Set[DateFrameId]] = None):
        if end_date is None:
            colliding_date_frames = list(
                filter(lambda pomodoro:
                       cls._check_if_excluded(pomodoro.id, excluded_date_frame_ids) and
                       cls._check_if_finished(pomodoro) and
                       cls._check_if_overlaps(pomodoro, start_date),
                       task.pomodoros)
            )
        else:
            colliding_date_frames = list(
                filter(lambda pomodoro:
                       cls._check_if_excluded(pomodoro.id, excluded_date_frame_ids) and
                       (cls._check_if_overlaps(pomodoro, start_date) or
                        cls._check_if_overlaps(pomodoro, end_date)), task.pomodoros))

        if len(colliding_date_frames):
            raise CollidingDateFrameFound
