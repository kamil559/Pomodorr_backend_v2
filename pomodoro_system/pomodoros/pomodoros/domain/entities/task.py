import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from pomodoros.domain.entities import SubTask, DateFrame, Project, Priority
from pomodoros.domain.value_objects import (
    TaskStatus,
    Ordering,
    PomodoroDuration,
    PomodoroRenewalInterval
)


@dataclass
class Task:
    id: Optional[uuid.UUID]
    name: str
    status: TaskStatus
    priority: Priority
    ordering: Ordering
    pomodoros_to_do: int
    pomodoro_length: PomodoroDuration
    due_date: datetime
    reminder_date: datetime
    renewal_interval: PomodoroRenewalInterval
    project: Project
    note: str
    created_at: datetime
    completed_at: datetime
    sub_tasks: Optional[List[SubTask]]
    date_frames: Optional[List[DateFrame]]

    @property
    def next_due_date(self) -> datetime:
        return self.due_date + self.renewal_interval
