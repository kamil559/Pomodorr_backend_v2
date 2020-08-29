from dataclasses import dataclass

from pomodoros.domain.entities import DateFrame
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.value_objects import FrameType


@dataclass
class Pause(DateFrame):
    frame_type = FrameType.TYPE_PAUSE
    pomodoro: Pomodoro
