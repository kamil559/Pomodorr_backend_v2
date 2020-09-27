from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from foundation.domain.entities.user import UserId
from foundation.value_objects import Priority
from pomodoros.domain.value_objects import Ordering, ProjectId


@dataclass
class Project:
    id: ProjectId
    name: str
    priority: Priority
    ordering: Ordering
    owner_id: UserId
    created_at: datetime
    deleted_at: Optional[datetime]

    @property
    def is_removed(self):
        return self.deleted_at is not None
