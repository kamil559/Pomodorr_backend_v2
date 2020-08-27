from datetime import datetime
from typing import Optional, List

from pomodoros.domain.entities import Task
from pomodoros.domain.exceptions import CollidingDateFramesFound
from pomodoros.domain.value_objects import DateFrameId


def check_for_colliding_date_frames(task: Task, start_date: datetime,
                                    end_date: Optional[datetime] = None,
                                    excluded_date_frame_ids: Optional[List[DateFrameId]] = None):
    if end_date is None:
        colliding_date_frames = list(
            filter(lambda date_frame:
                   date_frame.start < start_date and
                   date_frame.end is None and
                   date_frame.id not in excluded_date_frame_ids, task.date_frames))
    else:
        colliding_date_frames = list(
            filter(lambda date_frame:
                   date_frame.start < start_date and
                   date_frame.end is not None and
                   date_frame.end > end_date and
                   date_frame.id not in excluded_date_frame_ids, task.date_frames))

    if len(colliding_date_frames):
        raise CollidingDateFramesFound
