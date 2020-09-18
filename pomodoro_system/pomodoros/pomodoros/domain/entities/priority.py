from dataclasses import dataclass
from datetime import datetime

from pomodoros.domain.value_objects import PriorityLevel, Color, PriorityId
from users.domain.entities import AbstractUser


@dataclass
class Priority:
    id: PriorityId
    name: str
    priority_level: PriorityLevel
    color: Color
    owner: AbstractUser
    created_at: datetime
