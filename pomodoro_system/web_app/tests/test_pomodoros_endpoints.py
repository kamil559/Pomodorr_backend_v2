import pytest
from flask import testing
from pony.orm import db_session

from pomodoros_infrastructure.repositories import SQLPomodoroRepository


class TestBeginPomodoroAPI:
    @pytest.mark.xfail(reason='needs plugging in the authentication & authorization library')
    def test_begin_pomodoro_with_valid_data(self, client: testing.FlaskClient, orm_task):
        response = client.post(f'/pomodoros/{orm_task.id}/begin', headers={}, json={})

        assert response.status_code == 201

    @pytest.mark.xfail(reason='needs plugging in the authentication & authorization library')
    def test_begin_pomodoro_without_authentication(self, client: testing.FlaskClient, orm_task):
        response = client.post(f'/pomodoros/{orm_task.id}/begin', headers={}, json={})

        assert response.status_code == 401

    @pytest.mark.xfail(reason='needs plugging in the authentication & authorization library')
    def test_begin_pomodoro_with_non_authorized_user(self, client: testing.FlaskClient, orm_task):
        response = client.post(f'/pomodoros/{orm_task.id}/begin', headers={}, json={})

        assert response.status_code == 403


class TestPausePomodoroAPI:
    @db_session
    def test_pause_pomodoro_with_valid_data(self, client: testing.FlaskClient, started_orm_pomodoro):
        response = client.patch(f'/pomodoros/{started_orm_pomodoro.id}/pause', headers={}, json={})

        pomodoros_repo = SQLPomodoroRepository()
        fetched_pomodoro = pomodoros_repo.get(started_orm_pomodoro.id)

        assert response.status_code == 200
        assert len(fetched_pomodoro.contained_pauses) == 1
        assert fetched_pomodoro.current_pause is not None

    def test_pause_pomodoro_without_authentication(self):
        pass

    def test_pause_pomodoro_with_non_authorized_user(self):
        pass
