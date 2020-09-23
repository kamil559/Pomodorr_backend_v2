from dataclasses import dataclass
from datetime import timedelta

from pomodoros.domain.value_objects import PomodoroLength, BreakLength

Color: str


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
