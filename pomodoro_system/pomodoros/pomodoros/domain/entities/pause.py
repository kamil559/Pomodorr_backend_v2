from dataclasses import dataclass
from datetime import datetime

from pomodoros.domain.entities import DateFrame
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.exceptions import RelatedPomodoroIsAlreadyFinished
from pomodoros.domain.value_objects import FrameType


@dataclass
class Pause(DateFrame):
    frame_type = FrameType.TYPE_PAUSE
    pomodoro: Pomodoro

    def begin(self, start_date: datetime) -> None:
        self.pomodoro.check_related_task_is_already_finished()
        super(Pause, self).run_begin_date_frame_validations(start_date=start_date)
        self._check_related_pomodoro_is_already_finished()

        self.start_date = start_date

    def finish(self, end_date: datetime) -> None:
        self.pomodoro.check_related_task_is_already_finished()
        super(Pause, self).run_finish_date_frame_validations(end_date=end_date)
        self._check_related_pomodoro_is_already_finished()

        self.end_date = end_date

    def _check_related_pomodoro_is_already_finished(self) -> None:
        if all([self.pomodoro.start_date, self.pomodoro.start_date is not None,
                self.pomodoro.end_date, self.pomodoro.end_date is not None]):
            raise RelatedPomodoroIsAlreadyFinished
