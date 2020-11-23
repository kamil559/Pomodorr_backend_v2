import uuid

from flask import Flask, testing
from flask_jwt_extended import get_jti
from flask_security.confirmable import generate_confirmation_token
from flask_security.recoverable import generate_reset_password_token
from foundation.models import User, UserDateFrameDefinitionModel
from pony.orm import db_session, select
from web_app.authentication.models.token import Token


def test_register(client: testing.FlaskClient, user_data: dict):
    response = client.post(
        "/register",
        headers={"Content-type": "application/json"},
        json={"email": user_data["email"], "password": user_data["password"]},
    )

    assert response.status_code == 200


@db_session
def test_register_creates_user_date_frame_definition_after_user_insert(client: testing.FlaskClient, user_data: dict):
    response = client.post(
        "/register",
        headers={"Content-type": "application/json"},
        json={"email": user_data["email"], "password": user_data["password"]},
    )

    assert response.status_code == 200

    new_user_id = response.json["response"]["user"]["id"]
    user_date_frame_definition = UserDateFrameDefinitionModel.select().filter(user=new_user_id).get()

    assert user_date_frame_definition is not None


def test_login(client: testing.FlaskClient, project_owner):
    response = client.post(
        "/login",
        headers={"Content-type": "application/json"},
        json={"email": project_owner.email, "password": "Zaq1@WSXcde3$RFV"},
    )

    assert response.status_code == 200
    assert response.json["response"]["access_token"]
    assert response.json["response"]["refresh_token"]


def test_login_fails_for_banned_user(client: testing.FlaskClient, banned_user):
    response = client.post(
        "/login",
        headers={"Content-type": "application/json"},
        json={"email": banned_user.email, "password": "Zaq1@WSXcde3$RFV"},
    )

    assert response.status_code == 400


def test_cannot_login_with_unconfirmed_user(client: testing.FlaskClient, unconfirmed_user):
    response = client.post(
        "/login",
        headers={"Content-type": "application/json"},
        json={"email": unconfirmed_user.email, "password": unconfirmed_user.password},
    )

    assert response.status_code == 400
    assert response.json["response"]["errors"]["email"][0] == "Email requires confirmation."


def test_refresh_access_token(client: testing.FlaskClient, project_owner):
    login_response = client.post(
        "/login", headers={}, json={"email": project_owner.email, "password": "Zaq1@WSXcde3$RFV"}
    )

    refresh_response = client.post(
        "/refresh", headers={"Authorization": f'Bearer {login_response.json["response"]["refresh_token"]}'}, json={}
    )

    assert refresh_response.status_code == 200
    assert refresh_response.json["response"]["access_token"]


def test_refresh_access_token_fails_for_banned_user(
    client: testing.FlaskClient, banned_user, banned_user_refresh_token
):
    refresh_response = client.post(
        "/refresh", headers={"Authorization": f"Bearer {banned_user_refresh_token}"}, json={}
    )

    assert refresh_response.status_code == 401


def test_access_token_is_revoked_for_banned_user(client: testing.FlaskClient, banned_user_access_token):
    retrieve_tokens_response = client.get(
        "/tokens",
        json={},
        headers={"Content-type": "application/json", "Authorization": f"Bearer {banned_user_access_token}"},
    )

    assert retrieve_tokens_response.status_code == 401


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
            f"/reset/{reset_password_token}",
            json={"password": "ZxCvFr$#2!", "password_confirm": "ZxCvFr$#2!"},
            headers={"Content-type": "application/json"},
        )

    assert change_password_response.status_code == 200
    assert change_password_response.json["response"]["user"]["id"] == str(project_owner.id)


def test_change_password(app: Flask, client: testing.FlaskClient, project_owner, project_owner_authorization_token):
    change_password_response = client.post(
        "/change",
        json={"password": "Zaq1@WSXcde3$RFV", "new_password": "ZxCvFr$#2!", "new_password_confirm": "ZxCvFr$#2!"},
        headers={"Content-type": "application/json", "Authorization": project_owner_authorization_token},
    )

    assert change_password_response.status_code == 200
    assert change_password_response.json["response"]["user"]["id"] == str(project_owner.id)
    assert change_password_response.json["response"]["result"]


def test_logout(client: testing.FlaskClient, project_owner_authorization_token):
    logout_response = client.get(
        "/logout",
        json={},
        headers={"Content-type": "application/json", "Authorization": project_owner_authorization_token},
    )

    assert logout_response.status_code == 200


def test_access_token_is_unusable_after_logout(client: testing.FlaskClient, project_owner_authorization_token):
    client.get(
        "/logout",
        json={},
        headers={"Content-type": "application/json", "Authorization": project_owner_authorization_token},
    )

    retrieve_tokens_response = client.get(
        "/tokens",
        json={},
        headers={"Content-type": "application/json", "Authorization": project_owner_authorization_token},
    )

    assert retrieve_tokens_response.status_code == 401


@db_session
def test_revoke_token(app: Flask, client: testing.FlaskClient, project_owner_authorization_token):
    with app.test_request_context():
        jti = get_jti(project_owner_authorization_token.replace("Bearer ", ""))
    token_id = select(token.id for token in Token if token.jti == jti).get()

    revoke_response = client.patch(
        f"/tokens/{token_id}",
        json={"revoked": True},
        headers={"Content-type": "application/json", "Authorization": project_owner_authorization_token},
    )

    revoked_value = select(token.revoked for token in Token if token.jti == jti).get()

    assert revoke_response.status_code == 200
    assert revoked_value


@db_session
def test_revoked_token_is_unusable(app: Flask, client: testing.FlaskClient, project_owner_authorization_token):
    with app.test_request_context():
        jti = get_jti(project_owner_authorization_token.replace("Bearer ", ""))
    token_id = select(token.id for token in Token if token.jti == jti).get()

    client.patch(
        f"/tokens/{token_id}",
        json={"revoked": True},
        headers={"Content-type": "application/json", "Authorization": project_owner_authorization_token},
    )

    retrieve_tokens_response = client.get(
        "/tokens",
        json={},
        headers={"Content-type": "application/json", "Authorization": project_owner_authorization_token},
    )

    assert retrieve_tokens_response.status_code == 401


def test_revoke_non_existing_token_returns_not_found(client: testing.FlaskClient, project_owner_authorization_token):
    token_id = uuid.uuid4()

    revoke_response = client.patch(
        f"/tokens/{token_id}",
        json={"revoked": True},
        headers={"Content-type": "application/json", "Authorization": project_owner_authorization_token},
    )

    assert revoke_response.status_code == 404


@db_session
def test_revoke_token_with_non_authenticated_user(
    app: Flask, client: testing.FlaskClient, project_owner_authorization_token
):
    with app.test_request_context():
        jti = get_jti(project_owner_authorization_token.replace("Bearer ", ""))
    token_id = select(token.id for token in Token if token.jti == jti).get()

    revoke_response = client.patch(
        f"/tokens/{token_id}",
        json={"revoked": True},
        headers={},
    )

    assert revoke_response.status_code == 401


@db_session
def test_revoke_token_with_non_authorized_user(
    app: Flask, client: testing.FlaskClient, project_owner_authorization_token, random_project_owner_authorization_token
):
    with app.test_request_context():
        jti = get_jti(project_owner_authorization_token.replace("Bearer ", ""))
    token_id = select(token.id for token in Token if token.jti == jti).get()

    revoke_response = client.patch(
        f"/tokens/{token_id}",
        json={"revoked": True},
        headers={"Content-type": "application/json", "Authorization": random_project_owner_authorization_token},
    )

    assert revoke_response.status_code == 403


@db_session
def test_legalize_token(client: testing.FlaskClient, project_owner_revoked_token, project_owner_authorization_token):
    legalize_response = client.patch(
        f"/tokens/{str(project_owner_revoked_token.id)}",
        json={"revoked": False},
        headers={"Content-type": "application/json", "Authorization": project_owner_authorization_token},
    )

    revoked_value = select(token.revoked for token in Token if token.jti == project_owner_revoked_token.jti).get()

    assert legalize_response.status_code == 200
    assert not revoked_value


def test_legalize_non_existing_token_returns_not_found(client: testing.FlaskClient, project_owner_authorization_token):
    random_token_id = uuid.uuid4()

    legalize_response = client.patch(
        f"/tokens/{str(random_token_id)}",
        json={"revoked": False},
        headers={"Content-type": "application/json", "Authorization": project_owner_authorization_token},
    )

    assert legalize_response.status_code == 404


def test_legalized_token_is_usable(
    client: testing.FlaskClient,
    project_owner_access_token,
    project_owner_revoked_token,
    project_owner_authorization_token,
):
    client.patch(
        f"/tokens/{project_owner_revoked_token.id}",
        json={"revoked": False},
        headers={"Content-type": "application/json", "Authorization": project_owner_authorization_token},
    )

    retrieve_tokens_response = client.get(
        "/tokens",
        json={},
        headers={"Content-type": "application/json", "Authorization": f"Bearer {project_owner_access_token}"},
    )

    assert retrieve_tokens_response.status_code == 200


def test_legalize_token_with_non_authenticated_user(
    client: testing.FlaskClient, project_owner_revoked_token, random_project_owner_authorization_token
):
    legalize_response = client.patch(
        f"/tokens/{str(project_owner_revoked_token.id)}",
        json={"revoked": False},
        headers={},
    )

    assert legalize_response.status_code == 401


def test_legalize_token_with_non_authorized_user(
    client: testing.FlaskClient, project_owner_revoked_token, random_project_owner_authorization_token
):
    legalize_response = client.patch(
        f"/tokens/{str(project_owner_revoked_token.id)}",
        json={"revoked": False},
        headers={"Content-type": "application/json", "Authorization": random_project_owner_authorization_token},
    )

    assert legalize_response.status_code == 403
