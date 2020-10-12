import pytest
from pony.orm import db_session

from pomodoros_infrastructure.queries.tasks import SQLGetTasksByProjectId

pytestmark = pytest.mark.usefixtures("setup_teardown_tables")


def test_query_returns_tasks_by_project_id(orm_project, orm_task, orm_random_task):
    query_object = SQLGetTasksByProjectId()

    with db_session:
        result = query_object.query(orm_project.id)

    assert len(result) == 1
    assert orm_random_task.id != result[0].id
    assert orm_task.id == result[0].id
