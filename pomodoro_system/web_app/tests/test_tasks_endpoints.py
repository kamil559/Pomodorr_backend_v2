from flask import testing
from pony.orm import db_session

from pomodoros_infrastructure.repositories import SQLTaskRepository


class TestCompleteTaskAPI:
    @db_session
    def test_complete_task_with_valid_data(self, client: testing.FlaskClient, orm_task,
                                           project_owner_authorization_token):
        response = client.patch(f'/tasks/{orm_task.id}/complete',
                                headers={'Authorization': project_owner_authorization_token}, json={})

        task_repo = SQLTaskRepository()
        fetched_task = task_repo.get(orm_task.id)

        assert response.status_code == 200
        assert fetched_task.is_completed

    def test_complete_task_without_authorization_header(self, client: testing.FlaskClient, orm_task):
        response = client.patch(f'/tasks/{orm_task.id}/complete', headers={}, json={})

        assert response.status_code == 401

    def test_complete_task_with_random_authenticated_user(self, client: testing.FlaskClient, orm_task,
                                                          random_project_owner_authorization_token):
        response = client.patch(f'/tasks/{orm_task.id}/complete',
                                headers={'Authorization': random_project_owner_authorization_token}, json={})

        assert response.status_code == 403
