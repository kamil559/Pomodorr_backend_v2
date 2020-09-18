from dataclasses import dataclass
from datetime import datetime

from pomodoros.domain.entities import Task
from pomodoros.domain.value_objects import SubTaskId


@dataclass
class SubTask:
    id: SubTaskId
    name: str
    task: Task
    created_at: datetime
    is_completed: bool
