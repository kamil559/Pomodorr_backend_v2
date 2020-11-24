import re
import uuid
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from gettext import gettext as _
from typing import TypeVar

from foundation.exceptions import ValueValidationError

PomodoroLength = timedelta
BreakLength = timedelta
UserId = uuid.UUID
DefaultColorHex = "#d1d1d1"

T = TypeVar("T")


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

    @property
    def as_dict(self) -> dict:
        return {
            "pomodoro_length": self.pomodoro_length,
            "break_length": self.break_length,
            "longer_break_length": self.longer_break_length,
            "gap_between_long_breaks": self.gap_between_long_breaks,
        }


class PriorityLevel(Enum):
    NO_PRIORITY = 0
    LOW_PRIORITY = 1
    MID_PRIORITY = 2
    HIGH_PRIORITY = 3


@dataclass
class Color:
    hex: str = DefaultColorHex

    def clean(self) -> None:
        if self.hex != DefaultColorHex:
            if not isinstance(self.hex, str):
                raise ValueValidationError(_("Color type must be string."))

            if not re.compile("^#?((?:[0-F]{3}){1,2})$", re.IGNORECASE).match(self.hex):
                raise ValueValidationError(_("Invalid rgb hex value."))

    def __post_init__(self) -> None:
        self.clean()

    def __len__(self):
        return len(self.hex)


@dataclass
class Priority:
    color: Color = Color()
    priority_level: PriorityLevel = PriorityLevel.NO_PRIORITY
