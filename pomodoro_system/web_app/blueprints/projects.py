import http
from uuid import UUID

from flask import Response, g, jsonify, make_response, request
from flask_apispec import doc, marshal_with, use_kwargs
from flask_jwt_extended import get_jwt_identity, jwt_required
from foundation.exceptions import DomainValidationError
from marshmallow import ValidationError
from pomodoros import ProjectId, ProjectRepository
from pomodoros.application.queries.projects import GetProjectsByOwnerId
from pomodoros_infrastructure import ProjectModel
from web_app.authorization.projects import ProjectProtector
from web_app.docs_definitions.language import language_header_definition
from web_app.marshallers.projects import ProjectRestSchema
from web_app.utils import RegistrableBlueprint, load_int_query_parameter

projects_blueprint = RegistrableBlueprint("projects", __name__, url_prefix="/projects")


@doc(
    description="Get project with specified project_id.",
    params={**language_header_definition},
    tags=(projects_blueprint.name,),
)
@marshal_with(
    ProjectRestSchema(
        many=False,
    ),
    http.HTTPStatus.OK,
)
@projects_blueprint.route("/<uuid:project_id>", methods=["GET"])
@jwt_required
def get_project(
    project_id: ProjectId, project_protector: ProjectProtector, project_repository: ProjectRepository
) -> Response:
    project_protector.authorize(UUID(get_jwt_identity()), project_id)
    return (
        jsonify(
            ProjectRestSchema(
                many=False,
            ).dump(project_repository.get(project_id))
        ),
        http.HTTPStatus.OK,
    )


@doc(
    description="Get project list.",
    params={
        "page_size": {"in": "query", "required": False},
        "page": {"in": "query", "required": False},
        "sort": {
            "in": "query",
            "required": False,
            "type": "array",
            "items": {
                "type": "string",
            },
            "default": ["created_at", "ordering", "name"],
        },
    },
    tags=(projects_blueprint.name,),
)
@marshal_with(
    ProjectRestSchema(
        many=True,
    ),
    http.HTTPStatus.OK,
)
@projects_blueprint.route("/", methods=["GET"])
@jwt_required
def get_project_list(
    projects_by_owner_id_query: GetProjectsByOwnerId,
):
    g.sort_fields = {
        "name": ProjectModel.name,
        "ordering": ProjectModel.ordering,
        "created_at": ProjectModel.created_at,
    }
    g.default_sort_fields = ["created_at"]
    request_user_id = UUID(get_jwt_identity())
    return jsonify(
        ProjectRestSchema(
            many=True,
        ).dump(projects_by_owner_id_query.query(request_user_id))
    )


@doc(
    description="Create a new project.",
    tags=(projects_blueprint.name,),
)
@marshal_with(
    ProjectRestSchema(
        many=False,
    ),
    http.HTTPStatus.CREATED,
)
@use_kwargs(
    ProjectRestSchema(
        many=False,
    )
)
@projects_blueprint.route("/", methods=["POST"])
@jwt_required
def create_project(project_repository: ProjectRepository):
    try:
        request_user_id = get_jwt_identity()
        new_project = ProjectRestSchema(many=False, context={"owner_id": request_user_id}).load(request.json)
    except (DomainValidationError, ValidationError) as error:
        return jsonify(error.messages), http.HTTPStatus.BAD_REQUEST

    project_repository.save(new_project, create=True)
    return jsonify(ProjectRestSchema(many=False).dump(new_project)), http.HTTPStatus.CREATED


@doc(
    description="Update the project with project_id specified in url.",
    tags=(projects_blueprint.name,),
)
@marshal_with(
    ProjectRestSchema(
        many=False,
        partial=True,
    ),
    http.HTTPStatus.OK,
)
@use_kwargs(
    ProjectRestSchema(
        many=False,
        partial=True,
    )
)
@projects_blueprint.route("/<uuid:project_id>", methods=["PATCH"])
@jwt_required
def update_project(project_id: ProjectId, project_repository: ProjectRepository, project_protector: ProjectProtector):
    try:
        project_protector.authorize(UUID(get_jwt_identity()), project_id)
        project = project_repository.get(project_id)
        updated_project = ProjectRestSchema(many=False, partial=True, context={"project_instance": project}).load(
            request.json
        )
    except (DomainValidationError, ValidationError) as error:
        return jsonify(error.messages), http.HTTPStatus.BAD_REQUEST
    project_repository.save(updated_project)

    return jsonify(ProjectRestSchema(many=False).dump(updated_project)), http.HTTPStatus.OK


@doc(
    description="Delete the project with project_id specified in url.",
    tags=(projects_blueprint.name,),
)
@marshal_with(
    None,
    code=http.HTTPStatus.NO_CONTENT,
    description="The project with specified project_id in the url has been deleted.",
)
@projects_blueprint.route("/<uuid:project_id>", methods=["DELETE"])
@jwt_required
def delete_project(project_id: ProjectId, project_repository: ProjectRepository, project_protector: ProjectProtector):
    project_protector.authorize(UUID(get_jwt_identity()), project_id)
    permanently = bool(load_int_query_parameter(request.args.get("permanently")))
    project_repository.delete(project_id, permanently)

    return make_response("", http.HTTPStatus.NO_CONTENT)
