import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.value_objects import DateFrameDuration, FrameType, TaskId


@dataclass
class DateFrame:
    id: Optional[uuid.UUID]
    start: datetime
    end: datetime
    duration: DateFrameDuration
    frame_type: FrameType
    task_id: TaskId
