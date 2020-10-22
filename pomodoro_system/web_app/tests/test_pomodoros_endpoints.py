from flask import testing
from pony.orm import db_session

from pomodoros_infrastructure.repositories import SQLPomodoroRepository


class TestBeginPomodoroAPI:
    def test_begin_pomodoro_with_valid_data(self, client: testing.FlaskClient, orm_task,
                                            project_owner_authorization_token):
        response = client.post(f'/pomodoros/{orm_task.id}/begin',
                               headers={'Authorization': project_owner_authorization_token}, json={})

        assert response.status_code == 201

    def test_begin_pomodoro_without_authentication(self, client: testing.FlaskClient, orm_task):
        response = client.post(f'/pomodoros/{orm_task.id}/begin', headers={}, json={})

        assert response.status_code == 401

    def test_begin_pomodoro_with_non_authorized_user(self, client: testing.FlaskClient, orm_task,
                                                     random_project_owner_authorization_token):
        response = client.post(f'/pomodoros/{orm_task.id}/begin',
                               headers={'Authorization': random_project_owner_authorization_token}, json={})

        assert response.status_code == 403


class TestPausePomodoroAPI:
    @db_session
    def test_pause_pomodoro_with_valid_data(self, client: testing.FlaskClient, started_orm_pomodoro,
                                            project_owner_authorization_token):
        response = client.patch(f'/pomodoros/{started_orm_pomodoro.id}/pause',
                                headers={'Authorization': project_owner_authorization_token}, json={})

        pomodoros_repo = SQLPomodoroRepository()
        fetched_pomodoro = pomodoros_repo.get(started_orm_pomodoro.id)

        assert response.status_code == 200
        assert len(fetched_pomodoro.contained_pauses) == 1
        assert fetched_pomodoro.current_pause is not None

    def test_pause_pomodoro_without_authentication(self, client: testing.FlaskClient, started_orm_pomodoro, ):
        response = client.patch(f'/pomodoros/{started_orm_pomodoro.id}/pause', headers={}, json={})

        assert response.status_code == 401

    def test_pause_pomodoro_with_non_authorized_user(self, client: testing.FlaskClient, started_orm_pomodoro,
                                                     random_project_owner_authorization_token):
        response = client.patch(f'/pomodoros/{started_orm_pomodoro.id}/pause',
                                headers={'Authorization': random_project_owner_authorization_token}, json={})

        assert response.status_code == 403
