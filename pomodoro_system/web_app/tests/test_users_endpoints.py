from datetime import timedelta

import pytest
from flask import testing
from foundation.value_objects import UserDateFrameDefinition
from pony.orm import db_session
from web_app.users.repository import SQLUserRepository


class TestUserDataEndpoints:
    def test_get_user_data(self, client: testing.FlaskClient, project_owner_authorization_token):
        user_data_response = client.get("users/user_data", headers={"Authorization": project_owner_authorization_token})

        assert user_data_response.status_code == 200
        assert len(user_data_response.json) == 4
        assert all(value in user_data_response.json for value in {"avatar", "date_frame_definition", "email", "id"})

    def test_get_user_data_with_non_authenticated_user(self, client: testing.FlaskClient):
        user_data_response = client.get("users/user_data")

        assert user_data_response.status_code == 401

    def test_update_user_date_frame_definition_with_valid_data(
        self,
        client: testing.FlaskClient,
        project_owner,
        project_owner_authorization_token,
        user_date_frame_definition_update_data,
    ):
        update_user_data_response = client.patch(
            "users/user_data",
            headers={"Authorization": project_owner_authorization_token},
            json={"date_frame_definition": user_date_frame_definition_update_data},
        )

        assert update_user_data_response.status_code == 200
        with db_session:
            user_repository = SQLUserRepository()
            fetched_user = user_repository.get(project_owner.id)
            date_frame = fetched_user.date_frame_definition

            assert date_frame.break_length == timedelta(minutes=user_date_frame_definition_update_data["break_length"])
            assert date_frame.longer_break_length == timedelta(
                minutes=user_date_frame_definition_update_data["longer_break_length"]
            )
            assert date_frame.pomodoro_length == timedelta(
                minutes=user_date_frame_definition_update_data["pomodoro_length"]
            )
            assert (
                date_frame.gap_between_long_breaks == user_date_frame_definition_update_data["gap_between_long_breaks"]
            )
            assert date_frame.break_time_sound == user_date_frame_definition_update_data["break_time_sound"]
            assert date_frame.getting_to_work_sound == user_date_frame_definition_update_data["getting_to_work_sound"]

    @pytest.mark.parametrize(
        "date_frame_definition_data",
        [
            {
                "getting_to_work_sound": "",
                "break_time_sound": "",
            },
            {
                "getting_to_work_sound": None,
                "break_time_sound": None,
            },
            {
                "getting_to_work_sound": 1,
                "break_time_sound": 1,
            },
            {
                "getting_to_work_sound": "sound4",
                "break_time_sound": "sound4",
            },
        ],
    )
    def test_update_user_date_frame_definition_with_invalid_data(
        self, date_frame_definition_data, client: testing.FlaskClient, project_owner, project_owner_authorization_token
    ):
        update_user_data_response = client.patch(
            "users/user_data",
            headers={"Authorization": project_owner_authorization_token},
            json={"date_frame_definition": date_frame_definition_data},
        )

        assert update_user_data_response.status_code == 400
        assert "date_frame_definition" in update_user_data_response.json

    def test_update_user_with_non_authenticated_user(
        self, client: testing.FlaskClient, user_date_frame_definition_update_data
    ):
        update_user_data_response = client.patch(
            "users/user_data", json={"date_frame_definition": user_date_frame_definition_update_data}
        )

        assert update_user_data_response.status_code == 401

    def test_remove_avatar_clears_user_avatar(
        self,
        client: testing.FlaskClient,
        project_owner,
        project_owner_authorization_token,
        user_date_frame_definition_update_data,
    ):
        update_user_data_response = client.patch(
            "users/user_data",
            headers={"Authorization": project_owner_authorization_token},
            json={"remove_avatar": True},
        )

        assert update_user_data_response.status_code == 200
        with db_session:
            user_repository = SQLUserRepository()
            fetched_user = user_repository.get(project_owner.id)

            assert fetched_user.avatar == ""

    def test_clearing_date_frame_definition_values_assigns_default_values(
        self,
        client: testing.FlaskClient,
        project_owner,
        project_owner_authorization_token,
        user_date_frame_definition_update_data,
    ):
        update_user_data_response = client.patch(
            "users/user_data",
            headers={"Authorization": project_owner_authorization_token},
            json={"date_frame_definition": {}},
        )

        assert update_user_data_response.status_code == 200
        with db_session:
            user_repository = SQLUserRepository()
            fetched_user = user_repository.get(project_owner.id)
            date_frame = fetched_user.date_frame_definition

            assert date_frame.break_length == UserDateFrameDefinition.break_length
            assert date_frame.longer_break_length == UserDateFrameDefinition.longer_break_length
            assert date_frame.pomodoro_length == UserDateFrameDefinition.pomodoro_length
            assert date_frame.gap_between_long_breaks == UserDateFrameDefinition.gap_between_long_breaks
            assert date_frame.break_time_sound == UserDateFrameDefinition.break_time_sound
            assert date_frame.getting_to_work_sound == UserDateFrameDefinition.getting_to_work_sound
