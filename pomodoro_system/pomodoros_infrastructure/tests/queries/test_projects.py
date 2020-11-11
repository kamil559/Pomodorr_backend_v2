import uuid

import pytest
from pomodoros_infrastructure.queries.projects import SQLGetProjectsByOwnerId
from pony.orm import db_session


@pytest.mark.usefixtures("setup_teardown_tables")
class TestGetProjectsByOwnerIdQuery:
    @db_session
    def test_query_returns_projects_by_owner_id(self, project_owner, orm_project, orm_random_project):
        query_object = SQLGetProjectsByOwnerId()
        result_ids = list(map(lambda project: project.id, query_object.query(project_owner.id)))

        assert len(result_ids) == 1
        assert orm_project.id in result_ids

    @db_session
    def test_query_returns_empty_collection_if_owner_has_no_projects(self, project_owner, orm_random_project):
        query_object = SQLGetProjectsByOwnerId()
        result = query_object.query(project_owner.id)

        assert result == []

    @db_session
    def test_query_returns_empty_collection_if_non_existing_owner_id_was_passed(self, orm_project, orm_random_project):
        query_object = SQLGetProjectsByOwnerId()
        random_uuid = uuid.uuid4()
        result = query_object.query(random_uuid)

        assert result == []
