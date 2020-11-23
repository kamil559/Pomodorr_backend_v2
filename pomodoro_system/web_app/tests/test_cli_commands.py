from flask import Flask
from pony.orm import db_session
from web_app.commands import create_admin


@db_session
def test_add_new_admin_with_valid_data(app: Flask, user_datastore, user_data):
    runner = app.test_cli_runner()

    runner.invoke(create_admin, [user_data["email"], user_data["password"]])
    new_admin = user_datastore.find_user(email=user_data["email"])

    assert new_admin is not None
    assert new_admin.has_role("admin")


@db_session
def test_add_new_admin_with_invalid_data(app: Flask, user_datastore, user_data):
    runner = app.test_cli_runner()
    invalid_email = "xyz@xyz"

    runner.invoke(create_admin, [invalid_email, user_data["password"]])
    new_admin = user_datastore.find_user(email=invalid_email)

    assert new_admin is None


@db_session
def test_add_new_admin_with_existing_email_address(app: Flask, user_datastore, user_data, project_owner):
    runner = app.test_cli_runner()

    runner.invoke(create_admin, [project_owner.email, user_data["password"]])
    new_admin = user_datastore.find_user(email=project_owner.email)

    assert new_admin is not None
    assert not new_admin.has_role("admin")
