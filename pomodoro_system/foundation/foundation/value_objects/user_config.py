from dataclasses import dataclass

from pomodoros.domain.value_objects import PomodoroLength, BreakLength


@dataclass
class UserConfig:
    pomodoro_length: PomodoroLength
    break_length: BreakLength
