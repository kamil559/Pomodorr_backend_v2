from dataclasses import dataclass
from datetime import datetime

from foundation.value_objects.user import AbstractUser
from pomodoros.domain.value_objects import PriorityLevel, Color, PriorityId


@dataclass
class Priority:
    id: PriorityId
    name: str
    priority_level: PriorityLevel
    color: Color
    owner: AbstractUser
    created_at: datetime
