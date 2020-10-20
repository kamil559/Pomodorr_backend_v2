import datetime

import pytz


def contains_utc(date: datetime.datetime) -> bool:
    return date.tzinfo and (date.tzinfo == pytz.UTC or date.tzinfo == datetime.timezone.utc)


def to_utc(date: datetime.datetime) -> datetime.datetime:
    """
    The function translates passed in date into UTC only if its tzinfo is None or other than UTC
    :rtype: datetime
    """
    if contains_utc(date):
        return date
    return date.astimezone(tz=pytz.UTC)


def with_tzinfo(date: datetime.datetime, tz=pytz.UTC):
    if date is None:
        return
    return date.replace(tzinfo=tz)
