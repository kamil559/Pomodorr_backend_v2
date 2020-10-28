from flask import Flask, testing
from flask_security.confirmable import generate_confirmation_token
from flask_security.recoverable import generate_reset_password_token
from foundation.models import User
from pony.orm import db_session


def test_register(client: testing.FlaskClient, user_data: dict):
    response = client.post(
        "/register",
        headers={"Content-type": "application/json"},
        json={"email": user_data["email"], "password": user_data["password"]},
    )

    assert response.status_code == 200


def test_login(client: testing.FlaskClient, project_owner):
    response = client.post(
        "/login?include_auth_token=1",
        headers={"Content-type": "application/json"},
        json={"email": project_owner.email, "password": project_owner.password},
    )

    assert response.status_code == 200


def test_cannot_login_with_unconfirmed_user(client: testing.FlaskClient, unconfirmed_user):
    response = client.post(
        "/login?include_auth_token=1",
        headers={"Content-type": "application/json"},
        json={"email": unconfirmed_user.email, "password": unconfirmed_user.password},
    )

    assert response.status_code == 400
    assert response.json["response"]["errors"]["email"][0] == "Email requires confirmation."


def test_confirm_registration(app: Flask, client: testing.FlaskClient, unconfirmed_user):
    with app.test_request_context():
        confirm_token = generate_confirmation_token(unconfirmed_user)

        change_password_response = client.get(f"/confirm/{confirm_token}", headers={"Content-type": "application/json"})
        assert change_password_response.status_code == 302

    with db_session:
        fetched_user = User[unconfirmed_user.id]
        assert fetched_user.confirmed_at is not None


def test_recover_password(app: Flask, client: testing.FlaskClient, project_owner):
    with app.test_request_context():
        reset_password_token = generate_reset_password_token(project_owner)

        change_password_response = client.post(
            f"/reset/{reset_password_token}?include_auth_token=1",
            json={"password": "ZxCvFr$#2!", "password_confirm": "ZxCvFr$#2!"},
            headers={"Content-type": "application/json"},
        )

    assert change_password_response.status_code == 200
    assert change_password_response.json["response"]["user"]["id"] == str(project_owner.id)
    assert change_password_response.json["response"]["user"]["authentication_token"]


def test_change_password(app: Flask, client: testing.FlaskClient, project_owner, project_owner_authorization_token):
    change_password_response = client.post(
        "/change?include_auth_token=1",
        json={"password": "Zaq1@WSXcde3$RFV", "new_password": "ZxCvFr$#2!", "new_password_confirm": "ZxCvFr$#2!"},
        headers={"Content-type": "application/json", "Authorization": project_owner_authorization_token},
    )

    assert change_password_response.status_code == 200
    assert change_password_response.json["response"]["user"]["id"] == str(project_owner.id)
    assert change_password_response.json["response"]["user"]["authentication_token"]


def test_logout(client: testing.FlaskClient, project_owner_authorization_token):
    logout_response = client.get(
        "/logout",
        json={},
        headers={"Content-type": "application/json", "Authorization": project_owner_authorization_token},
    )

    assert logout_response.status_code == 302
