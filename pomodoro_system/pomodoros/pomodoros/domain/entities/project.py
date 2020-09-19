from dataclasses import dataclass
from datetime import datetime
from typing import List

from foundation.value_objects.user import AbstractUser
from pomodoros.domain.entities import Priority
from pomodoros.domain.entities.task import Task
from pomodoros.domain.value_objects import Ordering, ProjectId


@dataclass
class Project:
    id: ProjectId
    name: str
    priority: Priority
    ordering: Ordering
    owner: AbstractUser
    created_at: datetime
    tasks: List[Task]
