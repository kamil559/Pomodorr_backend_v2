import uuid
from datetime import timedelta
from enum import Enum

ProjectId = uuid.UUID
TaskId = uuid.UUID
SubTaskId = uuid.UUID
PomodoroId = uuid.UUID
PauseId = uuid.UUID

Ordering = int

PomodoroRenewalInterval = timedelta
DateFrameDuration = timedelta
AcceptablePomodoroErrorMargin: timedelta = timedelta(minutes=1)


class TaskStatus(Enum):
    ACTIVE = 0
    COMPLETED = 1


class FrameType(Enum):
    TYPE_POMODORO = 0
    TYPE_PAUSE = 1
