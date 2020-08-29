from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from pomodoros.domain.exceptions import FutureDateProvided, NaiveDateProvided, StartDateGreaterThanEndDate, \
    DateFrameAlreadyFinished
from pomodoros.domain.value_objects import DateFrameDuration, FrameType, DateFrameId


@dataclass
class DateFrame:
    id: Optional[DateFrameId]
    frame_type: FrameType
    start_date: Optional[datetime]
    end_date: Optional[datetime]

    def start(self, start_date: datetime) -> None:
        self._check_is_datetime_tz_aware(date=start_date)
        self._check_valid_date(date=start_date)

        self.start_date = start_date

    def finish(self, end_date: datetime) -> None:
        self._check_is_datetime_tz_aware(date=end_date)
        self._check_valid_date(date=end_date)
        self._check_start_date_greater_than_end_date(start_date=self.start_date, end_date=end_date)

        self.end_date = end_date

    @property
    def duration(self) -> DateFrameDuration:
        if self.start_date and self.end_date:
            return self.end_date - self.start_date
        return None

    @staticmethod
    def _check_is_datetime_tz_aware(date: datetime) -> None:
        if date.tzinfo is None:
            raise NaiveDateProvided

    @staticmethod
    def _check_valid_date(date: datetime) -> None:
        now: datetime = datetime.now(tz=timezone.utc)

        if date > now:
            raise FutureDateProvided

    def _check_date_frame_already_finished(self):
        if all([self.start_date, self.start_date is not None, self.end_date, self.end_date is not None]):
            raise DateFrameAlreadyFinished

    @staticmethod
    def _check_start_date_greater_than_end_date(start_date: datetime, end_date: datetime) -> None:
        if start_date > end_date:
            raise StartDateGreaterThanEndDate
