import uuid

import pytest
from pomodoros_infrastructure.queries.tasks import SQLGetRecentTasksByProjectId, SQLGetTaskListByOwnerId
from pony.orm import db_session


@pytest.mark.usefixtures("setup_teardown_tables")
class TestGetTaskByOwnerIdQuery:
    @db_session
    def test_query_returns_tasks_by_owner_id(self, project_owner, orm_project, orm_task, orm_random_task):
        query_object = SQLGetTaskListByOwnerId()
        result_ids = list(map(lambda task: task.id, query_object.query(project_owner.id)))

        assert len(result_ids) == 1
        assert orm_task.id in result_ids

    @db_session
    def test_query_returns_empty_collection_if_project_has_no_tasks(self, project_owner, orm_project):
        query_object = SQLGetTaskListByOwnerId()
        result = query_object.query(project_owner.id)

        assert result == []

    @db_session
    def test_query_returns_empty_collection_if_non_existing_project_id_was_passed(self):
        query_object = SQLGetTaskListByOwnerId()
        random_uuid = uuid.uuid4()
        result = query_object.query(random_uuid)

        assert result == []


@pytest.mark.usefixtures("setup_teardown_tables")
class TestSQLGetRecentTasksByProjectIdQuery:
    @db_session
    def test_query_returns_recent_tasks_filtered_by_project_id(
        self, orm_project, orm_task, orm_task_for_yesterday, orm_random_task
    ):
        query_object = SQLGetRecentTasksByProjectId()
        result_ids = list(map(lambda task: task.id, query_object.query(orm_project.id)))

        assert len(result_ids) == 1
        assert orm_task.id in result_ids

    @db_session
    def test_query_returns_empty_collection_if_project_does_not_contain_tasks(self, orm_project):
        query_object = SQLGetRecentTasksByProjectId()
        result = query_object.query(orm_project.id)

        assert result == []

    @db_session
    def test_query_returns_empty_collection_if_non_existing_project_id_was_passed(self):
        query_object = SQLGetRecentTasksByProjectId()
        random_uuid = uuid.uuid4()
        result = query_object.query(random_uuid)

        assert result == []
