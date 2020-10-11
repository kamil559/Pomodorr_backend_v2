from dataclasses import dataclass
from datetime import datetime

from pomodoros.domain.value_objects import SubTaskId, TaskId


@dataclass
class SubTask:
    id: SubTaskId
    name: str
    task_id: TaskId
    created_at: datetime
    is_completed: bool
