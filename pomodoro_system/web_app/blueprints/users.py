import http
from uuid import UUID

from flask import jsonify, request
from flask_apispec import doc, marshal_with, use_kwargs
from flask_jwt_extended import get_jwt_identity, jwt_required
from foundation.application.repositories.user import UserRepository
from foundation.exceptions import DomainValidationError
from foundation.value_objects import UserId
from marshmallow import ValidationError
from web_app.authorization.users import UserProtector
from web_app.docs_definitions.auth import auth_header_definition
from web_app.docs_definitions.language import language_header_definition
from web_app.marshallers.users import UserSchema
from web_app.utils import RegistrableBlueprint

date_frame_definitions_blueprint = RegistrableBlueprint("tasks", __name__, url_prefix="/date_frame_definitions")


@doc(
    description="Get user's data.",
    params={**auth_header_definition, **language_header_definition},
    tags=(date_frame_definitions_blueprint.name,),
)
@marshal_with(UserSchema, http.HTTPStatus.OK)
@date_frame_definitions_blueprint.route("/<uuid:user_id>", methods=["GET"])
@jwt_required
def get_user_data(user_id: UserId, user_protector: UserProtector, user_repository: UserRepository):
    # todo: return email, date_frame_definition,
    user_protector.authorize(UUID(get_jwt_identity()), user_id)
    return jsonify(UserSchema(many=False).dump(user_repository.get(user_id))), http.HTTPStatus.OK


@doc(
    description="Update user's data",
    params={**auth_header_definition, **language_header_definition},
    tags=(date_frame_definitions_blueprint.name,),
)
@marshal_with(UserSchema, http.HTTPStatus.OK)
@use_kwargs(UserSchema)
@date_frame_definitions_blueprint.route("/<uuid:user_id>", methods=["GET"])
@jwt_required
def update_user_data(user_id: UserId, user_protector: UserProtector, user_repository: UserRepository):
    user_protector.authorize(UUID(get_jwt_identity()), user_id)
    user = user_repository.get(user_id)

    try:
        updated_user = UserSchema(many=False, partial=True, context={"user_instance": user}).load(request.json)
    except (DomainValidationError, ValidationError) as error:
        return jsonify(error.messages), http.HTTPStatus.BAD_REQUEST
    user_repository.save(updated_user)

    return jsonify(UserSchema(many=False).dump(updated_user)), http.HTTPStatus.OK
