from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from pomodoros.domain.exceptions import FutureDateProvided, NaiveDateProvided, StartDateGreaterThanEndDate, \
    DateFrameIsAlreadyFinished
from pomodoros.domain.value_objects import DateFrameDuration, FrameType, DateFrameId


@dataclass
class DateFrame(ABC):
    id: Optional[DateFrameId]
    frame_type: FrameType
    start_date: Optional[datetime]
    end_date: Optional[datetime]

    def run_begin_date_frame_validations(self, start_date: datetime) -> None:
        self._check_is_datetime_tz_aware(date=start_date)
        self._check_valid_date(date=start_date)
        self._check_date_frame_already_finished()

    def run_finish_date_frame_validations(self, end_date: datetime) -> None:
        self._check_is_datetime_tz_aware(date=end_date)
        self._check_valid_date(date=end_date)
        self._check_date_frame_already_finished()
        self._check_start_date_greater_than_end_date(start_date=self.start_date, end_date=end_date)

    @abstractmethod
    def begin(self, start_date: datetime) -> None:
        pass

    @abstractmethod
    def finish(self, end_date: datetime) -> None:
        pass

    @property
    def duration(self) -> DateFrameDuration:
        if self.start_date and self.end_date:
            return self.end_date - self.start_date
        return None

    @staticmethod
    def _check_is_datetime_tz_aware(date: datetime) -> None:
        # todo: this should be checked on a lower level (preferably before assembling the input DTO)

        if date.tzinfo is None:
            raise NaiveDateProvided

    @staticmethod
    def _check_valid_date(date: datetime) -> None:
        # todo: this should be checked on a lower level (preferably before assembling the input DTO)

        now: datetime = datetime.now(tz=timezone.utc)

        if date > now:
            raise FutureDateProvided

    def _check_date_frame_already_finished(self):
        if all([self.start_date, self.start_date is not None, self.end_date, self.end_date is not None]):
            raise DateFrameIsAlreadyFinished

    @staticmethod
    def _check_start_date_greater_than_end_date(start_date: datetime, end_date: datetime) -> None:
        if start_date > end_date:
            raise StartDateGreaterThanEndDate
