from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from pomodoros.domain.entities import SubTask, Project, Priority
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.value_objects import (
    TaskStatus,
    Ordering,
    PomodoroLength,
    PomodoroRenewalInterval, BreakLength, TaskId
)


@dataclass
class Task:
    id: Optional[TaskId]
    name: str
    status: TaskStatus
    priority: Priority
    ordering: Ordering
    pomodoros_to_do: int
    pomodoro_length: Optional[PomodoroLength]
    break_length: Optional[BreakLength]
    due_date: datetime
    reminder_date: datetime
    renewal_interval: PomodoroRenewalInterval
    project: Project
    note: str
    created_at: datetime
    completed_at: datetime
    sub_tasks: Optional[List[SubTask]]
    pomodoros: Optional[List[Pomodoro]]

    @property
    def next_due_date(self) -> datetime:
        return self.due_date + self.renewal_interval

    @property
    def is_completed(self) -> bool:
        return self.status == TaskStatus.COMPLETED
