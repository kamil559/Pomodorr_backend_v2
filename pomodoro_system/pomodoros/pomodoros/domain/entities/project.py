from dataclasses import dataclass
from datetime import datetime

from foundation.entities.user import UserId
from pomodoros.domain.value_objects import Ordering, ProjectId, Priority


@dataclass
class Project:
    id: ProjectId
    name: str
    priority: Priority
    ordering: Ordering
    owner_id: UserId
    created_at: datetime
