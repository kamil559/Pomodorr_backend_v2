from datetime import datetime
from gettext import gettext as _
from typing import Optional

from pomodoros.domain.exceptions import DateFrameIsAlreadyFinished, StartDateGreaterThanEndDate
from pomodoros.domain.value_objects import FrameType


class DateFrame:
    frame_type: FrameType

    def __init__(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> None:
        self.start_date = start_date
        self.end_date = end_date

    @property
    def is_finished(self) -> bool:
        return all(
            [
                self.start_date,
                self.start_date is not None,
                self.end_date,
                self.end_date is not None,
            ]
        )

    def run_begin_date_frame_validations(self, start_date: datetime) -> None:
        pass

    def run_finish_date_frame_validations(self, end_date: datetime) -> None:
        self._check_date_frame_is_already_finished()
        self._check_start_date_greater_than_end_date(start_date=self.start_date, end_date=end_date)

    def _check_date_frame_is_already_finished(self) -> None:
        if all(
            [
                self.start_date,
                self.start_date is not None,
                self.end_date,
                self.end_date is not None,
            ]
        ):
            raise DateFrameIsAlreadyFinished(_("pomodoros.domain.entities.date_frame.date_frame_is_already_finished"))

    @staticmethod
    def _check_start_date_greater_than_end_date(start_date: datetime, end_date: datetime) -> None:
        if start_date > end_date:
            raise StartDateGreaterThanEndDate(
                _("pomodoros.domain.entities.date_frame.start_date_greater_than_end_date")
            )
