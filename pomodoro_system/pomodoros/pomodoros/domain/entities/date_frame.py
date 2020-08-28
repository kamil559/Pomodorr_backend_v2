import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from pomodoros.domain.entities import Task
from pomodoros.domain.exceptions import FutureDateProvided, NaiveDateProvided
from pomodoros.domain.value_objects import DateFrameDuration, FrameType


@dataclass
class DateFrame:
    id: Optional[uuid.UUID]
    frame_type: FrameType
    task: Task
    start: Optional[datetime] = None
    end: Optional[datetime] = None

    @property
    def duration(self) -> DateFrameDuration:
        if self.start and self.end:
            return self.end - self.start
        return None

    def start_date_frame(self, start_date: datetime) -> None:
        self._check_valid_date(utc_date=start_date)
        self.start = start_date

    def finish_date_frame(self, end_date: datetime) -> None:
        self._check_valid_date(utc_date=end_date)
        self.end = end_date

    @staticmethod
    def _check_valid_date(utc_date: datetime) -> None:
        now: datetime = datetime.now(tz=timezone.utc)

        if utc_date.tzinfo is None:
            raise NaiveDateProvided

        if utc_date > now:
            raise FutureDateProvided
