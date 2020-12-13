from dataclasses import dataclass
from typing import Optional

from pomodoros.domain.value_objects import Ordering, SubTaskId


@dataclass
class SubTask:
    id: Optional[SubTaskId]
    name: str
    ordering: Ordering
    is_completed: bool
