from datetime import timedelta
from enum import Enum

PriorityId = int
OwnerId = int
ProjectId: int
TaskId: int
PriorityLevel: int
Color: str
Ordering: int
PomodoroDuration: timedelta
PomodoroRenewalInterval: timedelta
DateFrameDuration: timedelta


class TaskStatus(Enum):
    ACTIVE = 0
    FINISHED = 1


class FrameType(Enum):
    TYPE_POMODORO = 0
    TYPE_BREAK = 1
    TYPE_PAUSE = 2
