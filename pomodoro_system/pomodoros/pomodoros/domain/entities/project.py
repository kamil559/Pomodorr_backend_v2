import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from pomodoros.domain.entities.task import Task
from pomodoros.domain.value_objects import PriorityId, OwnerId, Ordering


@dataclass
class Project:
    id: Optional[uuid.UUID]
    name: str
    priority_id: PriorityId
    ordering: Ordering
    owner_id: OwnerId
    created_at: datetime
    tasks: List[Task]
