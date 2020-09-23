from dataclasses import dataclass
from datetime import datetime
from typing import Optional

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
    deleted_at: Optional[datetime]

    @property
    def is_removed(self):
        return self.deleted_at is not None
