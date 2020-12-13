import http
from uuid import UUID

from flask import Response, jsonify, request
from flask_apispec import doc, marshal_with, use_kwargs
from flask_jwt_extended import get_jwt_identity, jwt_required
from foundation.application.repositories.user import UserRepository
from foundation.exceptions import DomainValidationError
from foundation.interfaces import MediaStorage
from marshmallow import ValidationError
from web_app.docs_definitions.language import language_header_definition
from web_app.marshallers.fields.file_field import FileField
from web_app.marshallers.users import UserSchema
from web_app.utils import RegistrableBlueprint

users_blueprint = RegistrableBlueprint("users", __name__, url_prefix="/users")


@doc(
    description="Get user's data.",
    params={**language_header_definition},
    tags=(users_blueprint.name,),
)
@marshal_with(UserSchema(exclude=("remove_avatar",)), http.HTTPStatus.OK)
@users_blueprint.route("/user_data", methods=["GET"])
@jwt_required
def get_user_data(user_repository: UserRepository) -> Response:
    user_id = UUID(get_jwt_identity())
    return jsonify(UserSchema(many=False).dump(user_repository.get(user_id))), http.HTTPStatus.OK


@doc(
    description="Update user's data",
    params={**language_header_definition},
    tags=(users_blueprint.name,),
)
@marshal_with(UserSchema(exclude=("remove_avatar",)), http.HTTPStatus.OK)
@use_kwargs(UserSchema(partial=True, exclude=("avatar",)))
@users_blueprint.route("/user_data", methods=["PATCH"])
@jwt_required
def update_user_data(user_repository: UserRepository, media_storage: MediaStorage) -> Response:
    user_id = UUID(get_jwt_identity())
    user = user_repository.get(user_id)

    try:
        updated_user = UserSchema(
            media_storage=media_storage, many=False, partial=True, exclude=("avatar",), context={"user_instance": user}
        ).load(request.json)
    except (DomainValidationError, ValidationError) as error:
        return jsonify(error.messages), http.HTTPStatus.BAD_REQUEST
    user_repository.save(updated_user)

    return jsonify(UserSchema(exclude=("remove_avatar",)).dump(updated_user)), http.HTTPStatus.OK


@doc(
    description="Update user's avatar by sending an image with 'multipart/form-data' form",
    params={**language_header_definition},
    tags=(users_blueprint.name,),
    consumes=["multipart/form-data"],
)
@marshal_with(UserSchema(only=("avatar",)), http.HTTPStatus.OK)
@use_kwargs(
    {"avatar": FileField(required=False, allow_none=True, retrieve_file_endpoint="users.retrieve_avatar", type="file")},
    location="files",
)
@users_blueprint.route("/update_avatar", methods=["PATCH"])
@jwt_required
def update_user_avatar(user_repository: UserRepository, media_storage: MediaStorage):
    user_id = UUID(get_jwt_identity())
    user = user_repository.get(user_id)

    try:
        updated_user = UserSchema(media_storage=media_storage, partial=True, context={"user_instance": user}).load(
            request.files
        )
    except (DomainValidationError, ValidationError) as error:
        return jsonify(error.messages), http.HTTPStatus.BAD_REQUEST
    user_repository.save(updated_user)

    return jsonify(UserSchema(only=("avatar",)).dump(updated_user)), http.HTTPStatus.OK


@doc(
    description="Retrieve user's avatar by providing the avatar's filename",
    params={**language_header_definition},
    tags=(users_blueprint.name,),
    responses={
        http.HTTPStatus.OK: {
            "content": {"image/*": {"schema": {"type": "string", "format": "binary"}}},
            "description": "The file has been found in the filesystem and returned back to the user.",
        },
        http.HTTPStatus.NOT_FOUND: {"description": "The file has not been found in the filesystem."},
    },
)
@users_blueprint.route("/avatars/<string:filename>", methods=["GET"])
@jwt_required
def retrieve_avatar(filename: str, media_storage: MediaStorage) -> Response:
    return media_storage.get_file("media/avatars", filename)
