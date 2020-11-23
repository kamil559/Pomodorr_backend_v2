import pytest
from flask import Flask
from foundation.exceptions import NotFound


def test_get_user(app: Flask, project_owner):
    datastore = app.extensions["security"].datastore
    user = datastore.get_user(project_owner.id, raise_if_not_found=True)

    assert user.id == project_owner.id


def test_get_user_with_banned_user_id(app: Flask, banned_user):
    datastore = app.extensions["security"].datastore

    with pytest.raises(NotFound):
        datastore.get_user(banned_user.id, raise_if_not_found=True)
