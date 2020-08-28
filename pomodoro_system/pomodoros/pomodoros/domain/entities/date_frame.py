import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pomodoros.domain.entities import Task
from pomodoros.domain.value_objects import DateFrameDuration, FrameType


@dataclass
class DateFrame:
    id: Optional[uuid.UUID]
    start: datetime
    end: Optional[datetime]
    frame_type: FrameType
    task: Task

    @property
    def duration(self) -> DateFrameDuration:
        if self.start and self.end:
            return self.end - self.start
        return None
