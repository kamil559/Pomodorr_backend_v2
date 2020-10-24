from datetime import datetime

import pytz
from flask import testing
from pony.orm import db_session

from pomodoros_infrastructure.repositories import SQLPomodoroRepository


class TestBeginPomodoroAPI:
    def test_begin_pomodoro_with_valid_data(
            self, client: testing.FlaskClient, orm_task, project_owner_authorization_token
    ):
        response = client.post(
            f"/pomodoros/{orm_task.id}/begin",
            headers={"Authorization": project_owner_authorization_token},
            json={},
        )

        assert response.status_code == 201

    def test_begin_pomodoro_without_authorization_header(self, client: testing.FlaskClient, orm_task):
        response = client.post(f"/pomodoros/{orm_task.id}/begin", headers={}, json={})

        assert response.status_code == 401

    def test_begin_pomodoro_with_random_authenticated_user(
            self,
            client: testing.FlaskClient,
            orm_task,
            random_project_owner_authorization_token,
    ):
        response = client.post(
            f"/pomodoros/{orm_task.id}/begin",
            headers={"Authorization": random_project_owner_authorization_token},
            json={},
        )

        assert response.status_code == 403


class TestPausePomodoroAPI:
    @db_session
    def test_pause_pomodoro_with_valid_data(
            self,
            client: testing.FlaskClient,
            started_orm_pomodoro,
            project_owner_authorization_token,
    ):
        response = client.post(
            f"/pomodoros/{started_orm_pomodoro.id}/pause",
            headers={"Authorization": project_owner_authorization_token},
            json={},
        )

        expected_start_date_utc_hour = datetime.now(tz=pytz.UTC).hour
        pomodoro_repo = SQLPomodoroRepository()
        fetched_pomodoro = pomodoro_repo.get(started_orm_pomodoro.id)

        assert response.status_code == 200
        assert len(fetched_pomodoro.contained_pauses) == 1
        assert fetched_pomodoro.current_pause is not None
        assert fetched_pomodoro.contained_pauses[-1].start_date.hour == expected_start_date_utc_hour

    def test_pause_pomodoro_without_authorization_header(self, client: testing.FlaskClient, started_orm_pomodoro):
        response = client.post(f"/pomodoros/{started_orm_pomodoro.id}/pause", headers={}, json={})

        assert response.status_code == 401

    def test_pause_pomodoro_with_random_authenticated_user(
            self,
            client: testing.FlaskClient,
            started_orm_pomodoro,
            random_project_owner_authorization_token,
    ):
        response = client.post(
            f"/pomodoros/{started_orm_pomodoro.id}/pause",
            headers={"Authorization": random_project_owner_authorization_token},
            json={},
        )

        assert response.status_code == 403


class TestResumePomodoroAPI:
    @db_session(optimistic=False)
    def test_resume_pomodoro_with_valid_data(
            self,
            client: testing.FlaskClient,
            paused_orm_pomodoro,
            project_owner_authorization_token,
    ):
        response = client.post(
            f"/pomodoros/{paused_orm_pomodoro.id}/resume",
            headers={"Authorization": project_owner_authorization_token},
            json={},
        )

        expected_end_date_utc_hour = datetime.now(tz=pytz.UTC).hour
        pomodoro_repo = SQLPomodoroRepository()
        fetched_pomodoro = pomodoro_repo.get(paused_orm_pomodoro.id)

        assert response.status_code == 200
        assert len(fetched_pomodoro.contained_pauses) == 1
        assert fetched_pomodoro.contained_pauses[-1].is_finished
        assert fetched_pomodoro.contained_pauses[-1].end_date.hour == expected_end_date_utc_hour

    def test_resume_pomodoro_without_authorization_header(self, client: testing.FlaskClient, paused_orm_pomodoro):
        response = client.post(f"/pomodoros/{paused_orm_pomodoro.id}/resume", headers={}, json={})

        assert response.status_code == 401

    def test_resume_pomodoro_with_random_authenticated_user(
            self,
            client: testing.FlaskClient,
            paused_orm_pomodoro,
            random_project_owner_authorization_token,
    ):
        response = client.post(
            f"/pomodoros/{paused_orm_pomodoro.id}/resume",
            headers={"Authorization": random_project_owner_authorization_token},
            json={},
        )

        assert response.status_code == 403


class TestFinishPomodoroAPI:
    @db_session
    def test_finish_pomodoro_with_valid_data(
            self,
            client: testing.FlaskClient,
            started_orm_pomodoro,
            project_owner_authorization_token,
    ):
        response = client.patch(
            f"/pomodoros/{started_orm_pomodoro.id}/finish",
            headers={"Authorization": project_owner_authorization_token},
            json={},
        )

        expected_end_date_utc_hour = datetime.now(tz=pytz.UTC).hour
        pomodoro_repo = SQLPomodoroRepository()
        fetched_pomodoro = pomodoro_repo.get(started_orm_pomodoro.id)

        assert response.status_code == 200
        assert fetched_pomodoro.is_finished
        assert fetched_pomodoro.end_date.hour == expected_end_date_utc_hour

    def test_finish_pomodoro_without_authorization_header(self, client: testing.FlaskClient, started_orm_pomodoro):
        response = client.patch(f"/pomodoros/{started_orm_pomodoro.id}/finish", headers={}, json={})

        assert response.status_code == 401

    def test_finish_pomodoro_with_random_authenticated_user(
            self,
            client: testing.FlaskClient,
            started_orm_pomodoro,
            random_project_owner_authorization_token,
    ):
        response = client.patch(
            f"/pomodoros/{started_orm_pomodoro.id}/finish",
            headers={"Authorization": random_project_owner_authorization_token},
            json={},
        )

        assert response.status_code == 403
