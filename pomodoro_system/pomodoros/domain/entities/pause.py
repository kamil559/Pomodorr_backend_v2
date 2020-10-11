from datetime import datetime
from typing import Optional

from pomodoros.domain.entities import DateFrame
from pomodoros.domain.value_objects import FrameType, PauseId


class Pause(DateFrame):
    frame_type = FrameType.TYPE_PAUSE

    def __init__(self, id: PauseId, start_date: datetime,
                 end_date: Optional[datetime] = None):
        super().__init__(start_date=start_date, end_date=end_date)
        self.id = id
