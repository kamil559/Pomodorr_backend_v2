import uuid
from datetime import timedelta
from enum import Enum

PriorityId = uuid.UUID
OwnerId = uuid.UUID
ProjectId: uuid.UUID
TaskId: uuid.UUID
SubTaskId: uuid.UUID
DateFrameId: uuid.UUID
PriorityLevel: int
Color: str
Ordering: int
PomodoroLength: timedelta
BreakLength: timedelta
PomodoroRenewalInterval: timedelta
DateFrameDuration: timedelta
PomodoroErrorMargin: timedelta = timedelta(minutes=1)


class TaskStatus(Enum):
    ACTIVE = 0
    COMPLETED = 1


class FrameType(Enum):
    TYPE_POMODORO = 0
    TYPE_PAUSE = 1
