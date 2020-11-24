import http
import uuid
from datetime import datetime
from gettext import gettext as _

from flask import Response, current_app, jsonify, make_response, request
from flask_apispec import doc, marshal_with, use_kwargs
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_raw_jwt,
    jwt_refresh_token_required,
    jwt_required,
)
from flask_security import ChangePasswordForm, LoginForm
from flask_security.changeable import change_user_password
from flask_security.utils import json_error_response, login_user, suppress_form_csrf
from foundation.exceptions import DomainValidationError
from foundation.utils import to_utc
from marshmallow import Schema, ValidationError, fields
from web_app.authentication.helpers import add_token_to_database, get_token, get_user_tokens, update_token
from web_app.authentication.marshallers import TokenSchema, UserBanRecordSchema, UserUnbanSchema
from web_app.authorization.decorators import roles_required
from web_app.authorization.token import TokenProtector
from web_app.docs_definitions.auth import auth_header_definition
from web_app.users.facade import UserFacade
from web_app.utils import RegistrableBlueprint, get_dto_or_abort
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
def login() -> Response:
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

        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)

        add_token_to_database(access_token)
        add_token_to_database(refresh_token)

        if user:
            payload.update(
                {
                    "user": user.get_security_payload(),
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            )

    return _security._render_json(payload, code, headers=None, user=user)


@doc(
    description="Logout by revoking the unexpired token.",
    params={**auth_header_definition},
    tags=(auth_blueprint.name,),
)
@marshal_with(None, http.HTTPStatus.OK, description="The token has been revoked ")
@auth_blueprint.route("/logout", methods=["GET"])
@jwt_required
def logout() -> Response:
    raw_token = get_raw_jwt()
    jti = raw_token.get("jti")

    token = get_token(jti=jti)
    update_token(token, {"revoked": True})

    return _security._render_json({"msg": _("You've been logged out.")}, http.HTTPStatus.OK, headers=None, user=None)


@doc(
    description="Change password.",
    params={**auth_header_definition},
    tags=(auth_blueprint.name,),
)
@marshal_with(ChangePasswordResponseSchema, http.HTTPStatus.OK)
@use_kwargs(ChangePasswordSchema(only=("password", "new_password", "new_password_confirm")))
@auth_blueprint.route("/change", methods=["POST"])
@jwt_required
def change_password() -> Response:
    form = ChangePasswordForm(MultiDict(request.get_json()), meta=suppress_form_csrf())
    user = _security.datastore.get_user(get_jwt_identity(), raise_if_not_found=True)

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
@auth_blueprint.route("/refresh", methods=["POST"])
@jwt_refresh_token_required
def refresh() -> Response:
    user = _security.datastore.get_user(get_jwt_identity(), raise_if_not_found=True)

    access_token = create_access_token(user)
    add_token_to_database(access_token)

    return _security._render_json({"access_token": access_token}, http.HTTPStatus.OK, headers=None, user=user)


@doc(
    description="Retrieve token list.",
    params={**auth_header_definition},
    tags=(auth_blueprint.name,),
)
@marshal_with(TokenSchema, http.HTTPStatus.OK)
@auth_blueprint.route("/tokens", methods=["GET"])
@jwt_required
def token_list() -> Response:
    tokens = TokenSchema(many=True).dump(get_user_tokens(get_jwt_identity()))
    return jsonify(tokens), http.HTTPStatus.OK


@doc(
    description="Revoke or legalize token by passing the boolean value for 'revoked' key.",
    params={**auth_header_definition},
    tags=(auth_blueprint.name,),
)
@marshal_with(TokenSchema, http.HTTPStatus.OK)
@use_kwargs(TokenSchema)
@auth_blueprint.route("/tokens/<uuid:token_id>", methods=["PATCH"])
@jwt_required
def revoke_or_legalize_token(token_id: uuid.UUID, token_protector: TokenProtector) -> Response:
    token_protector.authorize(uuid.UUID(get_jwt_identity()), token_id)
    try:
        token_data = TokenSchema(partial=True).load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), http.HTTPStatus.BAD_REQUEST
    else:
        token = get_token(id=token_id)
        updated_token = update_token(token, token_data)
        return jsonify(TokenSchema().dump(updated_token)), http.HTTPStatus.OK


@doc(
    description="Ban user for a given period of time or permanently.",
    params={**auth_header_definition},
    tags=(auth_blueprint.name,),
)
@marshal_with(UserBanRecordSchema, http.HTTPStatus.OK)
@use_kwargs(UserBanRecordSchema)
@auth_blueprint.route("/ban_user", methods=["POST"])
@jwt_required
@roles_required("admin")
def ban_user(user_facade: UserFacade) -> Response:
    try:
        ban_user_input_data = get_dto_or_abort(UserBanRecordSchema, {})
        ban_user_output_data = user_facade.ban_user(ban_user_input_data)
    except (ValidationError, DomainValidationError) as error:
        return make_response(jsonify(error.messages), http.HTTPStatus.BAD_REQUEST)
    return make_response(jsonify(UserBanRecordSchema().dump(ban_user_output_data)), http.HTTPStatus.OK)


@doc(
    description="Unban user with user_id specified in url.",
    params={**auth_header_definition},
    tags=(auth_blueprint.name,),
)
@marshal_with(UserUnbanSchema, http.HTTPStatus.OK)
@use_kwargs(UserUnbanSchema(exclude=("manually_unbanned_at",)))
@auth_blueprint.route("/unban_user", methods=["POST"])
@jwt_required
@roles_required("admin")
def unban_user(user_facade: UserFacade) -> Response:
    try:
        unban_user_input_data = get_dto_or_abort(
            UserUnbanSchema, context={"manually_unbanned_at": str(to_utc(datetime.now()))}
        )
        unban_user_output_data = user_facade.unban_user(unban_user_input_data)
    except (ValidationError, DomainValidationError) as error:
        return make_response(jsonify(error.messages), http.HTTPStatus.BAD_REQUEST)
    return make_response(jsonify(UserUnbanSchema().dump(unban_user_output_data)), http.HTTPStatus.OK)
