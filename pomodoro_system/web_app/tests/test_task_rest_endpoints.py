import uuid

import pytest
from flask import testing
from foundation.value_objects import Priority


class TestTaskRestMethods:
    def test_get_task(self, client: testing.FlaskClient, project_owner_authorization_token, orm_task):
        response = client.get(f"tasks/{orm_task.id}", headers={"Authorization": project_owner_authorization_token})

        assert response.status_code == 200

    def test_get_task_with_non_existing_task_id(self, client: testing.FlaskClient, project_owner_authorization_token):
        random_uuid = uuid.uuid4()
        response = client.get(
            f"tasks/{str(random_uuid)}/tasks", headers={"Authorization": project_owner_authorization_token}
        )

        assert response.status_code == 404

    def test_get_task_with_non_authenticated_user(self, client: testing.FlaskClient, orm_task):
        response = client.get(f"tasks/{orm_task.id}")

        assert response.status_code == 401

    def test_get_task_with_non_authorized_user(
        self, client: testing.FlaskClient, random_project_owner_authorization_token, orm_task
    ):
        response = client.get(
            f"tasks/{orm_task.id}", headers={"Authorization": random_project_owner_authorization_token}
        )

        assert response.status_code == 403

    def test_get_recent_tasks_list(
        self,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        orm_project,
        orm_task,
        orm_task_for_yesterday,
    ):
        response = client.get(
            f"tasks/{orm_project.id}/tasks", headers={"Authorization": project_owner_authorization_token}
        )

        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]["id"] == str(orm_task.id)

    def test_get_all_task_list(
        self,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        orm_project,
        orm_task,
        orm_task_for_yesterday,
    ):
        response = client.get(
            f"tasks/{orm_project.id}/tasks?fetch_all=1", headers={"Authorization": project_owner_authorization_token}
        )

        assert response.status_code == 200
        assert len(response.json) == 2

    @pytest.mark.parametrize(
        "page_size, page, expected_length", [(1, 1, 1), (1, 2, 1), (2, 1, 2), (2, 2, 0), (1, 3, 0)]
    )
    def test_get_paginated_task_list(
        self,
        page_size,
        page,
        expected_length,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        orm_project,
        orm_task,
        orm_second_task,
    ):
        response = client.get(
            f"tasks/{orm_project.id}/tasks?page_size={page_size}&page={page}",
            headers={"Authorization": project_owner_authorization_token},
        )

        assert response.status_code == 200
        assert len(response.json) == expected_length

    @pytest.mark.parametrize(
        "page_size, page, expected_length",
        [
            ("", 1, 2),
            (1, "", 2),
            ("", "", 2),
            ("xyz", "xyz", 2),
            (1, "null", 2),
            ("null", 1, 2),
        ],
    )
    def test_get_paginated_task_list_with_wrong_params_returns_default_task_list(
        self,
        page_size,
        page,
        expected_length,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        orm_project,
        orm_task,
        orm_second_task,
    ):
        response = client.get(
            f"tasks/{orm_project.id}/tasks?page_size={page_size}&page={page}",
            headers={"Authorization": project_owner_authorization_token},
        )

        assert response.status_code == 200
        assert len(response.json) == expected_length

    @pytest.mark.parametrize(
        "sort_field",
        [
            "name",
            "-name",
            "ordering",
            "-ordering",
            "pomodoros_to_do",
            "-pomodoros_to_do",
            "pomodoros_burn_down",
            "-pomodoros_burn_down",
        ],
    )
    def test_get_sorted_task_list(
        self,
        sort_field,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        orm_project,
        orm_task,
        orm_second_task,
    ):
        response = client.get(
            f"tasks/{orm_project.id}/tasks?sort={sort_field}",
            headers={"Authorization": project_owner_authorization_token},
        )

        clean_sort_field = sort_field.lstrip("-")
        first_response_task = response.json[0]
        first_sorted_task = sorted(
            [orm_task, orm_second_task],
            reverse=sort_field.startswith("-"),
            key=lambda task: getattr(task, clean_sort_field),
        )[0]

        assert response.status_code == 200
        assert first_response_task[clean_sort_field] == getattr(first_sorted_task, clean_sort_field)

    @pytest.mark.parametrize("sort_field", ["", 323, "xyz", b"xyz", "null"])
    def test_get_sorted_task_list_with_wrong_fields_returns_default_task_list(
        self,
        sort_field,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        orm_project,
        orm_task,
        orm_second_task,
    ):
        response = client.get(
            f"tasks/{orm_project.id}/tasks?sort={sort_field}",
            headers={"Authorization": project_owner_authorization_token},
        )

        default_sorted_tasks = sorted([orm_task, orm_second_task], key=lambda task: task.created_at)

        assert response.status_code == 200
        assert response.json[0]["id"] == str(default_sorted_tasks[0].id)

    def test_get_task_list_with_non_existing_project_id(
        self,
        client: testing.FlaskClient,
        project_owner_authorization_token,
    ):
        random_uuid = uuid.uuid4()
        response = client.get(
            f"tasks/{str(random_uuid)}/tasks", headers={"Authorization": project_owner_authorization_token}
        )

        assert response.status_code == 404

    def test_get_task_list_with_non_authenticated_user(
        self,
        client: testing.FlaskClient,
        orm_project,
        orm_task,
        orm_task_for_yesterday,
    ):
        response = client.get(f"tasks/{orm_project.id}/tasks", headers={})

        assert response.status_code == 401

    def test_get_task_list_with_non_authorized_user(
        self,
        client: testing.FlaskClient,
        random_project_owner_authorization_token,
        orm_project,
        orm_task,
        orm_task_for_yesterday,
    ):
        response = client.get(
            f"tasks/{orm_project.id}/tasks", headers={"Authorization": random_project_owner_authorization_token}
        )

        assert response.status_code == 403

    def test_create_task_with_valid_data(
        self, client: testing.FlaskClient, project_owner_authorization_token, task_data
    ):
        response = client.post(
            "tasks/",
            headers={
                "Authorization": project_owner_authorization_token,
            },
            json=task_data,
        )

        assert response.status_code == 201

    @pytest.mark.parametrize("date_frame_value, priority_value", [(None, None), (True, True)])
    def test_create_task_without_date_frame_definition_and_priority_keys(
        self,
        date_frame_value,
        priority_value,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        task_data,
    ):
        if not date_frame_value:
            task_data["date_frame_definition"] = date_frame_value
        else:
            task_data.pop("date_frame_definition")

        if not priority_value:
            task_data["priority"] = priority_value
        else:
            task_data.pop("priority")

        response = client.post(
            "tasks/",
            headers={
                "Authorization": project_owner_authorization_token,
            },
            json=task_data,
        )

        expected_priority_data = {"color": Priority.color, "priority_level": Priority.priority_level.value}

        assert response.status_code == 201
        assert response.json["date_frame_definition"] is None
        assert response.json["priority"] == expected_priority_data

    @pytest.mark.parametrize(
        "data_key, invalid_value",
        [
            (
                "date_frame_definition",
                {
                    "pomodoro_length": "",
                    "break_length": "",
                    "longer_break_length": "",
                    "gap_between_long_breaks": "",
                },
            ),
            (
                "date_frame_definition",
                {
                    "pomodoro_length": None,
                    "break_length": None,
                    "longer_break_length": None,
                    "gap_between_long_breaks": None,
                },
            ),
            ("date_frame_definition", ""),
            ("priority", {"color": "", "priority_level": ""}),
            ("priority", ""),
        ],
    )
    def test_create_task_with_invalid_data(
        self, data_key, invalid_value, client: testing.FlaskClient, project_owner_authorization_token, task_data
    ):
        task_data[data_key] = invalid_value
        response = client.post(
            "tasks/",
            headers={
                "Authorization": project_owner_authorization_token,
            },
            json=task_data,
        )

        assert response.status_code == 400
        assert response.json[data_key]

    def test_create_task_with_non_authenticated_user(self, client: testing.FlaskClient, task_data):
        response = client.post("tasks/", json=task_data)

        assert response.status_code == 401

    def test_create_task_with_non_authorized_user(
        self, client: testing.FlaskClient, random_project_owner_authorization_token, task_data
    ):
        response = client.post(
            "tasks/",
            headers={
                "Authorization": random_project_owner_authorization_token,
            },
            json=task_data,
        )

        assert response.status_code == 403

    def test_update_task_with_valid_data(
        self, client: testing.FlaskClient, project_owner_authorization_token, orm_task, task_data
    ):
        response = client.patch(
            f"tasks/{str(orm_task.id)}",
            headers={
                "Authorization": project_owner_authorization_token,
            },
            json=task_data,
        )

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "data_key, invalid_value",
        [
            (
                "date_frame_definition",
                {
                    "pomodoro_length": "",
                    "break_length": "",
                    "longer_break_length": "",
                    "gap_between_long_breaks": "",
                },
            ),
            (
                "date_frame_definition",
                {
                    "pomodoro_length": None,
                    "break_length": None,
                    "longer_break_length": None,
                    "gap_between_long_breaks": None,
                },
            ),
            ("date_frame_definition", ""),
            ("priority", {"color": "", "priority_level": ""}),
            ("priority", ""),
        ],
    )
    def test_update_task_with_invalid_data(
        self,
        data_key,
        invalid_value,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        orm_task,
        task_data,
    ):
        task_data[data_key] = invalid_value

        response = client.patch(
            f"tasks/{str(orm_task.id)}",
            headers={
                "Authorization": project_owner_authorization_token,
            },
            json=task_data,
        )

        assert response.status_code == 400
        assert response.json[data_key]

    def test_update_task_with_non_authenticated_user(self, client: testing.FlaskClient, orm_task, task_data):
        response = client.patch(f"tasks/{str(orm_task.id)}", json=task_data)

        assert response.status_code == 401

    def test_update_task_with_non_authorized_user(
        self, client: testing.FlaskClient, random_project_owner_authorization_token, orm_task, task_data
    ):
        response = client.patch(
            f"tasks/{str(orm_task.id)}",
            headers={
                "Authorization": random_project_owner_authorization_token,
            },
            json=task_data,
        )

        assert response.status_code == 403

    def test_delete_task(
        self,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        orm_task,
    ):
        response = client.delete(
            f"tasks/{str(orm_task.id)}",
            headers={
                "Authorization": project_owner_authorization_token,
            },
        )

        assert response.status_code == 204

    def test_delete_task_with_non_existing_task_id(
        self,
        client: testing.FlaskClient,
        project_owner_authorization_token,
    ):
        random_uud = uuid.uuid4()
        response = client.delete(
            f"tasks/{str(random_uud)}",
            headers={
                "Authorization": project_owner_authorization_token,
            },
        )

        assert response.status_code == 404

    def test_delete_task_with_non_authenticated_user(self, client: testing.FlaskClient, orm_task):

        response = client.delete(
            f"tasks/{orm_task.id}",
        )

        assert response.status_code == 401

    def test_delete_task_with_non_authorized_user(
        self,
        client: testing.FlaskClient,
        orm_task,
        random_project_owner_authorization_token,
    ):
        response = client.delete(
            f"tasks/{str(orm_task.id)}",
            headers={
                "Authorization": random_project_owner_authorization_token,
            },
        )

        assert response.status_code == 403
