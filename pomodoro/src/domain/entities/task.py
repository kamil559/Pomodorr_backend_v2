import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.value_objects import (TaskStatus, PriorityId, ProjectId, PomodoroDuration, PomodoroRenewalInterval,
                                      Ordering)


@dataclass
class Task:
    id: Optional[uuid.UUID]
    name: str
    status: TaskStatus
    priority_id: PriorityId
    ordering: Ordering
    remaining_pomodoros: int
    pomodoro_length: PomodoroDuration
    due_date: datetime
    reminder_date: datetime
    renewal_interval: PomodoroRenewalInterval
    project_id: ProjectId
    note: str
    created_at: datetime
