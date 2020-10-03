from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

Color = str
PomodoroLength = timedelta
BreakLength = timedelta


@dataclass
class DateFrameDefinition:
    pomodoro_length: PomodoroLength
    break_length: BreakLength
    longer_break_length: BreakLength
    gap_between_long_breaks: int


@dataclass
class UserDateFrameDefinition(DateFrameDefinition):
    pomodoro_length = timedelta(minutes=25)
    break_length = timedelta(minutes=5)
    longer_break_length = timedelta(minutes=15)
    gap_between_long_breaks = 3


class PriorityLevel(Enum):
    NO_PRIORITY = 0
    LOW_PRIORITY = 1
    MID_PRIORITY = 2
    HIGH_PRIORITY = 3


@dataclass
class Priority:
    color: Color = "#d1d1d1"
    priority_level: PriorityLevel = PriorityLevel.NO_PRIORITY
