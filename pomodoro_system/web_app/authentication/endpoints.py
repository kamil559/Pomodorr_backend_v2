import http
from gettext import gettext as _

from flask import current_app, request
from flask_apispec import doc, marshal_with, use_kwargs
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_refresh_token_required,
    jwt_required,
)
from flask_security import ChangePasswordForm, LoginForm
from flask_security.changeable import change_user_password
from flask_security.utils import json_error_response, login_user, suppress_form_csrf
from marshmallow import Schema, fields
from web_app.docs_definitions.auth import auth_header_definition
from web_app.utils import RegistrableBlueprint
from werkzeug.datastructures import MultiDict
from werkzeug.local import LocalProxy

auth_blueprint = RegistrableBlueprint(
    "auth",
    __name__,
)
_security = LocalProxy(lambda: current_app.extensions["security"])


class UserLookupSchema(Schema):
    id = fields.UUID(dump_only=True)


class ResponseMetaSchema(Schema):
    code = fields.Integer(description="Response status code metadata.")


class LoginSchema(Schema):
    email = fields.Email(load_only=True, required=True, allow_none=False)
    password = fields.String(load_only=True, required=True, allow_none=False)
    access_token = fields.String(dump_only=True)
    refresh_token = fields.String(dump_only=True)
    user = fields.Nested(UserLookupSchema, dump_only=True)


class LoginResponseSchema(Schema):
    meta = fields.Nested(ResponseMetaSchema)
    response = fields.Nested(LoginSchema(only=("access_token", "refresh_token", "user")))


class ChangePasswordSchema(Schema):
    password = fields.String(load_only=True, required=True, allow_none=False)
    new_password = fields.String(load_only=True, required=True, allow_none=False)
    new_password_confirm = fields.String(load_only=True, required=True, allow_none=False)
    result = fields.String(dump_only=True)
    user = fields.Nested(UserLookupSchema, dump_only=True)


class ChangePasswordResponseSchema(Schema):
    meta = fields.Nested(ResponseMetaSchema)
    response = fields.Nested(ChangePasswordSchema(only=("result", "user")))


@doc(
    description="Retrieve access and refresh token.",
    tags=(auth_blueprint.name,),
)
@marshal_with(LoginResponseSchema, http.HTTPStatus.OK)
@use_kwargs(LoginSchema)
@auth_blueprint.route("/login", methods=["POST"])
def login():
    form = LoginForm(MultiDict(request.get_json()), meta=suppress_form_csrf())

    if form.validate_on_submit():
        login_user(form.user, authn_via=["password"])

    errors = len(form.errors)
    user = form.user

    if errors:
        code = http.HTTPStatus.BAD_REQUEST
        payload = json_error_response(errors=form.errors)
    else:
        code = http.HTTPStatus.OK
        payload = {}

        if user:
            payload.update(
                {
                    "user": user.get_security_payload(),
                    "access_token": create_access_token(user),
                    "refresh_token": create_refresh_token(user),
                }
            )

    return _security._render_json(payload, code, headers=None, user=user)


@doc(
    description="Change password.",
    params={**auth_header_definition},
    tags=(auth_blueprint.name,),
)
@marshal_with(ChangePasswordResponseSchema, http.HTTPStatus.OK)
@use_kwargs(ChangePasswordSchema(only=("password", "new_password", "new_password_confirm")))
@auth_blueprint.route("/change", methods=["POST"])
@jwt_required
def change_password():
    form = ChangePasswordForm(MultiDict(request.get_json()), meta=suppress_form_csrf())
    user = _security.datastore.get_user(get_jwt_identity())

    if user:
        login_user(user)

    if form.validate_on_submit():
        change_user_password(user, form.new_password.data)

    errors = len(form.errors)

    if errors:
        code = http.HTTPStatus.BAD_REQUEST
        payload = json_error_response(errors=form.errors)
    else:
        code = http.HTTPStatus.OK
        payload = {}

        if user is not None:
            payload["user"] = user.get_security_payload()
            payload["result"] = _("The password has been changed successfully.")

    return _security._render_json(payload, code, headers=None, user=user)


@doc(
    description="Retrieve access based on the refresh token.",
    params={**auth_header_definition},
    tags=(auth_blueprint.name,),
)
@marshal_with(LoginSchema(only=("access_token",)), http.HTTPStatus.OK)
@use_kwargs({"refresh_token": fields.String(required=True, allow_none=False)})
@auth_blueprint.route("/refresh", methods=["POST"])
@jwt_refresh_token_required
def refresh():
    user = _security.datastore.get_user(get_jwt_identity())
    payload = {"access_token": create_access_token(user)}
    return _security._render_json(payload, http.HTTPStatus.OK, headers=None, user=user)
