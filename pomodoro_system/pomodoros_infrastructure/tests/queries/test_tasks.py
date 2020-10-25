import uuid

import pytest
from pomodoros_infrastructure.queries.tasks import SQLGetTasksByProjectId
from pony.orm import db_session


@pytest.mark.usefixtures("setup_teardown_tables")
class TestGetTaskByProjectIdQuery:
    @db_session
    def test_query_returns_tasks_by_project_id(self, orm_project, orm_task, orm_random_task):
        query_object = SQLGetTasksByProjectId()
        result = query_object.query(orm_project.id)

        assert len(result) == 1
        assert orm_random_task.id != result[0].id
        assert orm_task.id == result[0].id

    @db_session
    def test_query_returns_empty_collection_if_project_has_no_tasks(self, orm_project):
        query_object = SQLGetTasksByProjectId()
        result = query_object.query(orm_project.id)

        assert result == []

    @db_session
    def test_query_returns_empty_collection_if_non_existing_project_id_was_passed(self):
        query_object = SQLGetTasksByProjectId()
        random_uuid = uuid.uuid4()
        result = query_object.query(random_uuid)

        assert result == []
