from datetime import datetime, timedelta
from typing import Tuple

import pytest
import pytz
from pomodoros_infrastructure import PauseModel, PomodoroModel, TaskModel
from pomodoros_infrastructure.tests.factories import (ORMPauseFactory,
                                                      ORMPomodoroFactory,
                                                      ORMTaskFactory)
from pony.orm import db_session


@pytest.fixture()
def yesterday_date_range() -> Tuple[datetime, datetime]:
    yesterday = datetime.now(tz=pytz.UTC) - timedelta(days=1)
    return yesterday.replace(hour=10, minute=00), yesterday.replace(hour=10, minute=25)


@pytest.fixture()
def today_date_range() -> Tuple[datetime, datetime]:
    today = datetime.now(tz=pytz.UTC)
    return today.replace(hour=10, minute=00), today.replace(hour=10, minute=25)


@pytest.fixture()
def orm_random_task() -> TaskModel:
    with db_session:
        return ORMTaskFactory()


@pytest.fixture()
def orm_pomodoro(orm_task: TaskModel) -> PomodoroModel:
    with db_session:
        return ORMPomodoroFactory(task_id=orm_task.id)


@pytest.fixture()
def orm_random_pomodoro_for_today(today_date_range: Tuple[datetime, datetime]) -> PomodoroModel:
    with db_session:
        start_date, end_date = today_date_range
        return ORMPomodoroFactory(start_date=start_date, end_date=end_date)


@pytest.fixture()
def orm_pomodoro_for_today(orm_task: TaskModel, today_date_range: Tuple[datetime, datetime]) -> PomodoroModel:
    with db_session:
        start_date, end_date = today_date_range
        return ORMPomodoroFactory(task_id=orm_task.id, start_date=start_date, end_date=end_date)


@pytest.fixture()
def orm_random_pomodoro_for_yesterday(yesterday_date_range: Tuple[datetime, datetime]) -> PomodoroModel:
    with db_session:
        start_date, end_date = yesterday_date_range
        return ORMPomodoroFactory(start_date=start_date, end_date=end_date)


@pytest.fixture()
def orm_pomodoro_for_yesterday(orm_task: TaskModel, yesterday_date_range: Tuple[datetime, datetime]) -> PomodoroModel:
    with db_session:
        start_date, end_date = yesterday_date_range
        return ORMPomodoroFactory(task_id=orm_task.id, start_date=start_date, end_date=end_date)


@pytest.fixture()
def orm_pause() -> PauseModel:
    with db_session:
        return ORMPauseFactory()
