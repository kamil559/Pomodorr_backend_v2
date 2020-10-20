import datetime
from typing import Optional

import pytz


def contains_utc(date: datetime.datetime) -> bool:
    return date.tzinfo and (date.tzinfo == pytz.UTC or date.tzinfo == datetime.timezone.utc)


def to_utc(date: datetime.datetime) -> Optional[datetime.datetime]:
    if date is None:
        return
    if contains_utc(date):
        return date
    return date.astimezone(tz=pytz.UTC)


def with_tzinfo(date: datetime.datetime, tz=pytz.UTC):
    if date is None:
        return
    return date.replace(tzinfo=tz)
