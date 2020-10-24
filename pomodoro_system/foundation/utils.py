from datetime import datetime, timezone
from typing import Optional, Union

import pytz
from pytz import BaseTzInfo


def contains_utc(date: datetime) -> bool:
    return bool(date.tzinfo and (date.tzinfo == pytz.UTC or date.tzinfo == timezone.utc))


def to_utc(date: datetime) -> Optional[datetime]:
    if date is None:
        return
    if contains_utc(date):
        return date
    return date.astimezone(tz=pytz.UTC)


def with_tzinfo(date: datetime, tz_info: Union[BaseTzInfo, timezone] = pytz.UTC) -> datetime:
    if date is None:
        return
    return date.replace(tzinfo=tz_info)
