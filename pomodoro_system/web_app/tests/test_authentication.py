from flask import testing


def test_register(client: testing.FlaskClient, user_data: dict):
    response = client.post(
        "/register",
        headers={"Content-type": "application/json"},
        json={"email": user_data["email"], "password": user_data["password"]},
    )

    assert response.status_code == 200


def test_login(client: testing.FlaskClient, project_owner):
    response = client.post(
        "/login",
        headers={"Content-type": "application/json"},
        json={"email": project_owner.email, "password": project_owner.password},
    )

    assert response.status_code == 200


def test_cannot_login_with_unconfirmed_user(client: testing.FlaskClient, unconfirmed_user):
    response = client.post(
        "/login",
        headers={"Content-type": "application/json"},
        json={"email": unconfirmed_user.email, "password": unconfirmed_user.password},
    )

    assert response.status_code == 400
    assert response.json["response"]["errors"]["email"][0] == "Email requires confirmation."
