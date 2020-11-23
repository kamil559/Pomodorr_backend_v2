from datetime import datetime

import click
from flask import current_app
from flask.cli import AppGroup
from flask_security import UserDatastore, hash_password
from foundation.utils import to_utc
from marshmallow import Schema, ValidationError, fields, validates_schema
from pony.orm import db_session

user_cli = AppGroup("users")


class CreateAdminSchema(Schema):
    email = fields.Email(required=True, allow_none=False)
    password = fields.String(required=True, allow_none=False)

    def __init__(self, datastore: UserDatastore, *args, **kwargs) -> None:
        self.datastore = datastore
        super(CreateAdminSchema, self).__init__(*args, **kwargs)

    @validates_schema
    def validate(self, data: dict, **_kwargs) -> None:
        email = data["email"]
        password = data["password"]

        existing_user = self.datastore.find_user(email=email)
        if existing_user is not None:
            raise ValidationError(f"Email {email} already exists.")

        self.save_admin(email, password)

    def save_admin(self, email: str, password: str) -> None:
        user = self.datastore.create_user(
            email=email, password=hash_password(password), confirmed_at=to_utc(datetime.now()), active=True
        )
        admin_role = self.datastore.find_role("admin")
        self.datastore.add_role_to_user(user, admin_role)


@user_cli.command("create_admin")
@click.argument("email")
@click.argument("password")
@db_session
def create_admin(email: str, password: str) -> None:
    datastore = current_app.extensions["security"].datastore
    try:
        CreateAdminSchema(datastore=datastore).load({"email": email, "password": password})
    except ValidationError as error:
        click.echo(error.messages)
        return None
    else:
        click.echo(f"Admin {email} has been created successfully.")
