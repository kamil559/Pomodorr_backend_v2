import uuid

import pytest
from flask import testing
from foundation.value_objects import Priority
from pomodoros_infrastructure import ProjectModel
from pony.orm import db_session


class TestProjectsRestAPI:
    def test_get_project(self, client: testing.FlaskClient, project_owner_authorization_token, orm_project):
        response = client.get(
            f"projects/{orm_project.id}", headers={"Authorization": project_owner_authorization_token}
        )

        assert response.status_code == 200

    def test_get_project_with_non_existing_project_id(
        self, client: testing.FlaskClient, project_owner_authorization_token
    ):
        random_uuid = uuid.uuid4()
        response = client.get(
            f"projects/{str(random_uuid)}", headers={"Authorization": project_owner_authorization_token}
        )

        assert response.status_code == 404

    def test_get_project_with_non_authenticated_user(self, client: testing.FlaskClient, orm_project):
        response = client.get(f"projects/{orm_project.id}")

        assert response.status_code == 401

    def test_get_project_with_non_authorized_user(
        self, client: testing.FlaskClient, random_project_owner_authorization_token, orm_project
    ):
        response = client.get(
            f"projects/{orm_project.id}", headers={"Authorization": random_project_owner_authorization_token}
        )

        assert response.status_code == 403

    def test_get_project_list(
        self,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        orm_project,
        orm_second_project,
        orm_random_project,
    ):
        response = client.get("projects/", headers={"Authorization": project_owner_authorization_token})

        assert response.status_code == 200
        assert len(response.json) == 2

    @pytest.mark.parametrize(
        "page_size, page, expected_length", [(1, 1, 1), (1, 2, 1), (2, 1, 2), (2, 2, 0), (1, 3, 0)]
    )
    def test_get_paginated_project_list(
        self,
        page_size,
        page,
        expected_length,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        orm_project,
        orm_second_project,
        orm_random_project,
    ):
        response = client.get(
            f"projects/?page_size={page_size}&page={page}",
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
    def test_get_paginated_project_list_with_wrong_params_returns_default_project_list(
        self,
        page_size,
        page,
        expected_length,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        orm_project,
        orm_second_project,
        orm_random_project,
    ):
        response = client.get(
            f"projects/?page_size={page_size}&page={page}",
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
            "created_at",
            "-created_at",
        ],
    )
    def test_get_sorted_project_list(
        self,
        sort_field,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        orm_project,
        orm_second_project,
    ):
        response = client.get(
            f"projects/?sort={sort_field}",
            headers={"Authorization": project_owner_authorization_token},
        )

        clean_sort_field = sort_field.lstrip("-")
        first_response_project = response.json[0]
        first_sorted_project = sorted(
            [orm_project, orm_second_project],
            reverse=sort_field.startswith("-"),
            key=lambda project: getattr(project, clean_sort_field),
        )[0]

        assert response.status_code == 200
        assert first_response_project["id"] == str(first_sorted_project.id)

    @pytest.mark.parametrize("sort_field", ["", 323, "xyz", b"xyz", "null"])
    def test_get_sorted_project_list_with_wrong_fields_returns_default_project_list(
        self,
        sort_field,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        orm_project,
        orm_second_project,
    ):
        response = client.get(
            f"projects/?sort={sort_field}",
            headers={"Authorization": project_owner_authorization_token},
        )

        default_sorted_project = sorted([orm_project, orm_second_project], key=lambda project: project.created_at)

        assert response.status_code == 200
        assert response.json[0]["id"] == str(default_sorted_project[0].id)

    def test_get_project_list_with_non_authenticated_user(
        self,
        client: testing.FlaskClient,
        orm_project,
        orm_second_project,
    ):
        response = client.get("projects/", headers={})

        assert response.status_code == 401

    def test_create_project_with_valid_data(
        self, client: testing.FlaskClient, project_owner_authorization_token, project_data
    ):
        response = client.post(
            "projects/",
            headers={
                "Authorization": project_owner_authorization_token,
            },
            json=project_data,
        )

        assert response.status_code == 201

    def test_create_project_without_priority_key_saves_default_values(
        self,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        project_data,
    ):
        project_data["priority"] = None

        response = client.post(
            "projects/",
            headers={
                "Authorization": project_owner_authorization_token,
            },
            json=project_data,
        )

        expected_priority_data = {"color": Priority.color.hex, "priority_level": Priority.priority_level.value}

        assert response.status_code == 201
        assert response.json["priority"] == expected_priority_data

    @db_session
    def test_create_project_saves_authenticated_user_as_owner(
        self,
        client: testing.FlaskClient,
        project_owner,
        random_project_owner,
        project_owner_authorization_token,
        project_data,
    ):
        project_data["owner_id"] = str(random_project_owner.id)
        response = client.post(
            "projects/",
            headers={
                "Authorization": project_owner_authorization_token,
            },
            json=project_data,
        )
        fetched_project = ProjectModel[response.json["id"]]

        assert response.status_code == 201
        assert fetched_project.owner.id == project_owner.id

    @pytest.mark.parametrize(
        "data_key, invalid_value",
        [
            ("priority", {"color": "", "priority_level": ""}),
            ("priority", ""),
        ],
    )
    def test_create_project_with_invalid_data(
        self, data_key, invalid_value, client: testing.FlaskClient, project_owner_authorization_token, project_data
    ):
        project_data[data_key] = invalid_value
        response = client.post(
            "projects/",
            headers={
                "Authorization": project_owner_authorization_token,
            },
            json=project_data,
        )

        assert response.status_code == 400
        assert response.json[data_key]

    def test_create_project_with_non_authenticated_user(self, client: testing.FlaskClient, project_data):
        response = client.post("projects/", json=project_data)

        assert response.status_code == 401

    def test_update_project_with_valid_data(
        self, client: testing.FlaskClient, project_owner_authorization_token, orm_project, project_data
    ):
        response = client.patch(
            f"projects/{str(orm_project.id)}",
            headers={
                "Authorization": project_owner_authorization_token,
            },
            json=project_data,
        )

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "data_key, invalid_value",
        [
            ("priority", {"color": "", "priority_level": ""}),
            ("priority", ""),
        ],
    )
    def test_update_project_with_invalid_data(
        self,
        data_key,
        invalid_value,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        orm_project,
        project_data,
    ):
        project_data[data_key] = invalid_value

        response = client.patch(
            f"projects/{str(orm_project.id)}",
            headers={
                "Authorization": project_owner_authorization_token,
            },
            json=project_data,
        )

        assert response.status_code == 400
        assert response.json[data_key]

    def test_update_project_with_non_authenticated_user(self, client: testing.FlaskClient, orm_project, project_data):
        response = client.patch(f"projects/{str(orm_project.id)}", json=project_data)

        assert response.status_code == 401

    def test_update_project_with_non_authorized_user(
        self, client: testing.FlaskClient, random_project_owner_authorization_token, orm_project, project_data
    ):
        response = client.patch(
            f"projects/{str(orm_project.id)}",
            headers={
                "Authorization": random_project_owner_authorization_token,
            },
            json=project_data,
        )

        assert response.status_code == 403

    @db_session
    def test_soft_delete_project(
        self,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        orm_project,
    ):
        response = client.delete(
            f"projects/{str(orm_project.id)}",
            headers={
                "Authorization": project_owner_authorization_token,
            },
        )
        fetched_project = ProjectModel[orm_project.id]

        assert response.status_code == 204
        assert fetched_project.is_removed

    @db_session
    def test_delete_project_permanently(
        self,
        client: testing.FlaskClient,
        project_owner_authorization_token,
        orm_project,
    ):
        response = client.delete(
            f"projects/{str(orm_project.id)}?permanently=1",
            headers={
                "Authorization": project_owner_authorization_token,
            },
        )
        fetched_project_exists = ProjectModel.exists(id=orm_project.id)

        assert response.status_code == 204
        assert not fetched_project_exists

    def test_delete_project_with_non_existing_project_id(
        self,
        client: testing.FlaskClient,
        project_owner_authorization_token,
    ):
        random_uud = uuid.uuid4()
        response = client.delete(
            f"projects/{str(random_uud)}",
            headers={
                "Authorization": project_owner_authorization_token,
            },
        )

        assert response.status_code == 404

    def test_delete_project_with_non_authenticated_user(self, client: testing.FlaskClient, orm_project):
        response = client.delete(
            f"projects/{str(orm_project.id)}",
        )

        assert response.status_code == 401

    def test_delete_project_with_non_authorized_user(
        self,
        client: testing.FlaskClient,
        orm_project,
        random_project_owner_authorization_token,
    ):
        response = client.delete(
            f"projects/{str(orm_project.id)}",
            headers={
                "Authorization": random_project_owner_authorization_token,
            },
        )

        assert response.status_code == 403
