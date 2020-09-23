import uuid
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

from foundation.value_objects import Color

ProjectId: uuid.UUID
TaskId: uuid.UUID
SubTaskId: uuid.UUID
PomodoroId: uuid.UUID
PauseId: uuid.UUID

Ordering: int
PomodoroLength: timedelta
BreakLength: timedelta
PomodoroRenewalInterval: timedelta
DateFrameDuration: timedelta
AcceptablePomodoroErrorMargin: timedelta = timedelta(minutes=1)


class TaskStatus(Enum):
    ACTIVE = 0
    COMPLETED = 1


class FrameType(Enum):
    TYPE_POMODORO = 0
    TYPE_PAUSE = 1


class PriorityLevel(Enum):
    NO_PRIORITY = 0
    LOW_PRIORITY = 1
    MID_PRIORITY = 2
    HIGH_PRIORITY = 3


@dataclass
class Priority:
    color: Color
    priority_level: PriorityLevel = PriorityLevel.NO_PRIORITY
