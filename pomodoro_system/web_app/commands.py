from datetime import datetime

import click
from flask import current_app
from flask_security import hash_password
from foundation.utils import to_utc
from pony.orm import db_session


@click.argument("email")
@click.argument("password")
@db_session
def create_admin(email: str, password: str):
    datastore = current_app.extensions["security"].datastore
    existing_user = datastore.find_user(email=email)

    if existing_user is not None:
        print(f"Admin with email {email} already exists.")
        return None

    user = datastore.create_user(
        email=email, password=hash_password(password), confirmed_at=to_utc(datetime.now()), active=True
    )
    admin_role = datastore.find_role("admin")

    datastore.add_role_to_user(user, admin_role)
    print(f"Admin {email} has been created")
