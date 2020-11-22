import os
from datetime import datetime, timezone
from typing import Optional, Union

import pytz
from pytz import BaseTzInfo


def contains_utc(date: datetime) -> bool:
    return bool(date.tzinfo and (date.tzinfo == pytz.UTC or date.tzinfo == timezone.utc))


def to_utc(date_time: datetime) -> Optional[datetime]:
    if date_time is None:
        return
    if contains_utc(date_time):
        return date_time
    return date_time.astimezone(tz=pytz.UTC)


def with_tzinfo(date_time: datetime, tz_info: Union[BaseTzInfo, timezone] = pytz.UTC) -> datetime:
    if date_time is None:
        return
    return date_time.replace(tzinfo=tz_info)


def get_config_file_path(env_name: str) -> str:
    if env_name is None:
        return

    config_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.environ.get(env_name))
    )

    return config_path
