import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pomodoros.domain.value_objects import PriorityLevel, Color, OwnerId


@dataclass
class Priority:
    id: Optional[uuid.UUID]
    name: str
    priority_level: PriorityLevel
    color: Color
    owner_id: OwnerId
    created_at: datetime
