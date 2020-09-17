import operator
from datetime import datetime, timedelta
from functools import reduce

from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.exceptions import PomodoroErrorMarginExceeded
from pomodoros.domain.value_objects import PomodoroErrorMargin


def check_pomodoro_length(pomodoro: Pomodoro, end_date: datetime) -> None:
    pomodoro_duration = end_date - pomodoro.start_date
    pauses_duration = reduce(operator.add,
                             (pause.end_date - pause.end_date for pause in pomodoro.contained_pauses),
                             timedelta(0))

    total_duration = pomodoro_duration - pauses_duration
    duration_difference = total_duration - pomodoro.maximal_duration

    if duration_difference > PomodoroErrorMargin:
        raise PomodoroErrorMarginExceeded
