import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pomodoros.domain.entities import Task


@dataclass
class SubTask:
    id: Optional[uuid.UUID]
    name: str
    task: Task
    created_at: datetime
    is_completed: bool
