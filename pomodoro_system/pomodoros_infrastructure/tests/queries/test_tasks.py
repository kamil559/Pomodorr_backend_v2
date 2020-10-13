import uuid

import pytest
from pony.orm import db_session

from pomodoros_infrastructure.queries.tasks import SQLGetTasksByProjectId


@pytest.mark.usefixtures("setup_teardown_tables")
class TestGetTaskByProjectIdQuery:
    def test_query_returns_tasks_by_project_id(self, orm_project, orm_task, orm_random_task):
        query_object = SQLGetTasksByProjectId()

        with db_session:
            result = query_object.query(orm_project.id)

        assert len(result) == 1
        assert orm_random_task.id != result[0].id
        assert orm_task.id == result[0].id

    def test_query_returns_none_if_project_has_no_tasks(self, orm_project):
        query_object = SQLGetTasksByProjectId()

        with db_session:
            result = query_object.query(orm_project.id)

        assert result is None

    def test_query_returns_none_if_non_existing_project_id_was_passed(self):
        query_object = SQLGetTasksByProjectId()
        random_uuid = uuid.uuid4()

        with db_session:
            result = query_object.query(random_uuid)

        assert result is None
