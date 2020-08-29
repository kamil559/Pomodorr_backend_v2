import operator
from datetime import datetime, timedelta
from functools import reduce
from typing import Optional, Set

from pomodoros.domain.entities import Task, DateFrame
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.exceptions import CollidingDateFrameFound, PomodoroErrorMarginExceeded
from pomodoros.domain.value_objects import DateFrameId, PomodoroErrorMargin


def _date_is_lower_than_start(date_frame: DateFrame, start_date: datetime) -> bool:
    return date_frame.start_date > start_date


def _date_is_lower_than_end(date_frame: DateFrame, end_date: datetime) -> bool:
    return date_frame.end_date > end_date


def _date_frame_is_not_excluded(pomodoro: Pomodoro, excluded_date_frame_ids: Set[DateFrameId]) -> bool:
    return pomodoro.id not in excluded_date_frame_ids


def _finished_pomodoro_overlaps(date_frame: DateFrame, checked_date: datetime) -> bool:
    return date_frame.start_date is not None and date_frame.end_date is not None and \
           (date_frame.start_date > checked_date or date_frame.end_date > checked_date)


def check_for_colliding_pomodoros(task: Task, start_date: datetime,
                                  end_date: Optional[datetime] = None,
                                  excluded_date_frame_ids: Optional[Set[DateFrameId]] = None):
    if end_date is None:
        colliding_date_frames = list(
            filter(lambda pomodoro:
                   _date_frame_is_not_excluded(pomodoro, excluded_date_frame_ids) and
                   _finished_pomodoro_overlaps(pomodoro, start_date),
                   task.pomodoros)
        )
    else:
        colliding_date_frames = list(
            filter(lambda pomodoro:
                   _date_frame_is_not_excluded(pomodoro, excluded_date_frame_ids) and
                   (_finished_pomodoro_overlaps(pomodoro, start_date) or
                    _finished_pomodoro_overlaps(pomodoro, end_date)), task.pomodoros))

    if len(colliding_date_frames):
        raise CollidingDateFrameFound


def check_pomodoro_length(pomodoro: Pomodoro, end_date: datetime) -> None:
    pomodoro_duration = end_date - pomodoro.start_date
    pauses_duration = reduce(operator.add,
                             (pause.end_date - pause.end_date for pause in pomodoro.contained_pauses),
                             timedelta(0))

    total_duration = pomodoro_duration - pauses_duration
    duration_difference = total_duration - pomodoro.maximal_duration

    if duration_difference > PomodoroErrorMargin:
        raise PomodoroErrorMarginExceeded
