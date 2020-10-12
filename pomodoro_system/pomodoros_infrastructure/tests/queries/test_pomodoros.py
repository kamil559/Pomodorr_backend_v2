import pytest
from pony.orm import db_session

from pomodoros_infrastructure.queries.pomodoros import SQLGetRecentPomodoros

pytestmark = pytest.mark.usefixtures("setup_teardown_tables")


def test_get_recent_pomodoros_returns_pomodoro_from_today(orm_task, orm_pomodoro_for_today, orm_pomodoro_for_yesterday):
    query_object = SQLGetRecentPomodoros()
    with db_session:
        result = query_object.query(orm_task.id)

    assert len(result) == 1
    assert orm_pomodoro_for_yesterday.id != result[0].id
    assert orm_pomodoro_for_today.id == result[0].id


def test_get_recent_pomodoros_returns_task_related_pomodoros_only(orm_task, orm_pomodoro_for_today,
                                                                  orm_random_pomodoro_for_today,
                                                                  orm_pomodoro_for_yesterday,
                                                                  orm_random_pomodoro_for_yesterday):
    query_object = SQLGetRecentPomodoros()
    with db_session:
        result = query_object.query(orm_task.id)

    assert len(result) == 1
    assert orm_pomodoro_for_yesterday.id != result[0].id
    assert orm_random_pomodoro_for_yesterday.id != result[0].id
    assert orm_random_pomodoro_for_today.id != result[0].id
    assert orm_pomodoro_for_today.id == result[0].id
