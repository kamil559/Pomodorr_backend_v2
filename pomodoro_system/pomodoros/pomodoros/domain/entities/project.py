import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from pomodoros.domain.entities import Priority
from pomodoros.domain.entities.task import Task
from pomodoros.domain.value_objects import Ordering
from users.domain.entities import AbstractUser


@dataclass
class Project:
    id: Optional[uuid.UUID]
    name: str
    priority: Priority
    ordering: Ordering
    owner: AbstractUser
    created_at: datetime
    tasks: List[Task]
