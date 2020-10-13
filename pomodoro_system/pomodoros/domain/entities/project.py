from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from foundation.value_objects import Priority, UserId
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

    def __eq__(self, other) -> bool:
        return type(self) is type(other) and self.__dict__ == other.__dict__
