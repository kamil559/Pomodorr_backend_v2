import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pomodoros.pomodoros.domain import (
    TaskStatus,
    PomodoroDuration,
    PomodoroRenewalInterval,
    Ordering,
    ProjectId,
    PriorityId
)


@dataclass
class Task:
    id: Optional[uuid.UUID]
    name: str
    status: TaskStatus
    priority_id: PriorityId
    ordering: Ordering
    pomodoros_to_do: int
    pomodoro_length: PomodoroDuration
    due_date: datetime
    reminder_date: datetime
    renewal_interval: PomodoroRenewalInterval
    project_id: ProjectId
    note: str
    created_at: datetime
