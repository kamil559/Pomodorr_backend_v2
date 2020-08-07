import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pomodoros.domain.value_objects import TaskId


@dataclass
class SubTask:
    id: Optional[uuid.UUID]
    name: str
    task_id: TaskId
    created_at: datetime
    is_completed: bool
