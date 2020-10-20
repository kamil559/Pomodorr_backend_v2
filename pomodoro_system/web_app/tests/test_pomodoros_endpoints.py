import pytest
from flask import testing


@pytest.mark.usefixtures("setup_teardown_tables")
class TestPomodorosEndpoints:
    @pytest.mark.xfail(reason='needs plugging in the authentication & authorization library')
    def test_begin_pomodoro_with_valid_data(self, client: testing.FlaskClient, orm_task):
        response = client.post(
            f'/pomodoros/{orm_task.id}/begin', headers={}, json={}
        )

        assert response.status_code == 201

    @pytest.mark.xfail(reason='needs plugging in the authentication & authorization library')
    def test_begin_pomodoro_without_authentication(self, client: testing.FlaskClient, orm_task):
        response = client.post(
            f'/pomodoros/{orm_task.id}/begin', headers={}, json={}
        )

        assert response.status_code == 401

    @pytest.mark.xfail(reason='needs plugging in the authentication & authorization library')
    def test_begin_pomodoro_with_non_authorized_user(self, client: testing.FlaskClient, orm_task):
        response = client.post(
            f'/pomodoros/{orm_task.id}/begin', headers={}, json={}
        )

        assert response.status_code == 403
