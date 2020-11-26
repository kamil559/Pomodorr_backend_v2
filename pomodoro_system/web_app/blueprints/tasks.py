import http
from datetime import datetime
from uuid import UUID

from flask import Response, g, jsonify, make_response, request
from flask_apispec import doc, marshal_with, use_kwargs
from flask_jwt_extended import get_jwt_identity, jwt_required
from foundation.exceptions import DomainValidationError
from foundation.utils import to_utc
from marshmallow import ValidationError
from pomodoros import (
    CompleteTask,
    CompleteTaskInputDto,
    CompleteTaskOutputBoundary,
    GetTaskListByOwnerId,
    PinTaskToProject,
    PinTaskToProjectInputDto,
    PinTaskToProjectOutputBoundary,
    ReactivateTask,
    ReactivateTaskInputDto,
    ReactivateTaskOutputBoundary,
    TaskId,
    TaskRepository,
)
from pomodoros_infrastructure import TaskModel
from web_app.authorization.projects import ProjectProtector
from web_app.authorization.tasks import TaskProtector
from web_app.docs_definitions.auth import auth_header_definition
from web_app.docs_definitions.language import language_header_definition
from web_app.marshallers.tasks import (
    CompleteTaskSchema,
    PinTaskToProjectSchema,
    ReactivateTaskSchema,
    TaskFilterSchema,
    TaskRestSchema,
)
from web_app.utils import RegistrableBlueprint, get_dto_or_abort

tasks_blueprint = RegistrableBlueprint("tasks", __name__, url_prefix="/tasks")


@doc(
    description="Get task with specified task_id.",
    params={**auth_header_definition, **language_header_definition},
    tags=(tasks_blueprint.name,),
)
@marshal_with(TaskRestSchema(many=False), http.HTTPStatus.OK)
@tasks_blueprint.route("/<uuid:task_id>", methods=["GET"])
@jwt_required
def get_task(task_id: TaskId, task_repository: TaskRepository, task_protector: TaskProtector) -> Response:
    task_protector.authorize(UUID(get_jwt_identity()), task_id)
    return jsonify(TaskRestSchema(many=False).dump(task_repository.get(task_id))), http.HTTPStatus.OK


@doc(
    description="Get task list for a project_id specified in url.",
    params={
        **auth_header_definition,
        "page_size": {"in": "query", "required": False},
        "page": {"in": "query", "required": False},
        "sort": {
            "in": "query",
            "required": False,
            "type": "array",
            "items": {
                "type": "string",
            },
            "default": ["created_at", "ordering", "name", "pomodoros_to_do", "pomodoros_burn_down"],
        },
    },
    tags=(tasks_blueprint.name,),
)
@use_kwargs(TaskFilterSchema, location="query")
@marshal_with(TaskRestSchema(many=True), http.HTTPStatus.OK)
@tasks_blueprint.route("/", methods=["GET"])
@jwt_required
def get_task_list(
    get_task_list_by_owner_id_query: GetTaskListByOwnerId,
) -> Response:
    current_user = UUID(get_jwt_identity())
    g.sort_fields = {
        "ordering": TaskModel.ordering,
        "created_at": TaskModel.created_at,
        "name": TaskModel.name,
        "pomodoros_to_do": TaskModel.pomodoros_to_do,
        "pomodoros_burn_down": TaskModel.pomodoros_burn_down,
    }
    g.default_sort_fields = ["created_at"]

    try:
        filter_fields = TaskFilterSchema().load(request.args)
    except ValidationError as error:
        filter_fields = error.valid_data

    result = get_task_list_by_owner_id_query.query(
        owner_id=current_user, return_full_entity=True, filter_fields=filter_fields
    )

    return jsonify(TaskRestSchema(many=True).dump(result)), http.HTTPStatus.OK


@doc(
    description="Create a new task within a project_id specified in url.",
    params={
        **auth_header_definition,
    },
    tags=(tasks_blueprint.name,),
)
@marshal_with(TaskRestSchema(many=False), http.HTTPStatus.CREATED)
@use_kwargs(TaskRestSchema(many=False))
@tasks_blueprint.route("/", methods=["POST"])
@jwt_required
def create_task(project_protector: ProjectProtector, task_repository: TaskRepository) -> Response:
    try:
        new_task = TaskRestSchema(many=False).load(request.json)
        project_protector.authorize(UUID(get_jwt_identity()), new_task.project_id, abort_request=False)
    except (DomainValidationError, ValidationError) as error:
        return jsonify(error.messages), http.HTTPStatus.BAD_REQUEST

    task_repository.save(new_task, create=True)
    return jsonify(TaskRestSchema(many=False).dump(new_task)), http.HTTPStatus.CREATED


@doc(
    description="Update the task with task_id specified in url.",
    params={
        **auth_header_definition,
    },
    tags=(tasks_blueprint.name,),
)
@marshal_with(TaskRestSchema(many=False, partial=True), http.HTTPStatus.OK)
@use_kwargs(TaskRestSchema(many=False, partial=True, exclude=("project_id",)))
@tasks_blueprint.route("/<uuid:task_id>", methods=["PATCH"])
@jwt_required
def update_task(task_id: TaskId, task_protector: TaskProtector, task_repository: TaskRepository) -> Response:
    try:
        task_protector.authorize(UUID(get_jwt_identity()), task_id)
        task = task_repository.get(task_id)
        updated_task = TaskRestSchema(
            many=False, partial=True, exclude=("project_id",), context={"task_instance": task}
        ).load(request.json)
    except (DomainValidationError, ValidationError) as error:
        return jsonify(error.messages), http.HTTPStatus.BAD_REQUEST
    task_repository.save(updated_task)

    return jsonify(TaskRestSchema(many=False).dump(updated_task)), http.HTTPStatus.OK


@doc(
    description="Delete the task with task_id specified in url.",
    params={
        **auth_header_definition,
    },
    tags=(tasks_blueprint.name,),
)
@marshal_with(
    None, code=http.HTTPStatus.NO_CONTENT, description="The task with specified task_id in the url has been deleted."
)
@tasks_blueprint.route("/<uuid:task_id>", methods=["DELETE"])
@jwt_required
def delete_task(task_id: TaskId, task_protector: TaskProtector, task_repository: TaskRepository) -> Response:
    task_protector.authorize(UUID(get_jwt_identity()), task_id)
    task_repository.delete(task_id)

    return make_response("", http.HTTPStatus.NO_CONTENT)


@doc(
    description="Marks the task with specified task_id complete.",
    params={**auth_header_definition, **language_header_definition},
    tags=(tasks_blueprint.name,),
)
@marshal_with(
    CompleteTaskSchema,
    http.HTTPStatus.OK,
    description="{new_task_id} is returned only if a repeatable task was completed.",
)
@tasks_blueprint.route("/<uuid:task_id>/complete", methods=["PATCH"])
@jwt_required
def complete_task(
    task_id: TaskId,
    complete_task_uc: CompleteTask,
    presenter: CompleteTaskOutputBoundary,
    protector: TaskProtector,
) -> Response:
    input_dto: CompleteTaskInputDto = get_dto_or_abort(
        CompleteTaskSchema,
        {"id": task_id, "completed_at": str(to_utc(datetime.now()))},
    )

    protector.authorize(UUID(get_jwt_identity()), task_id)

    complete_task_uc.execute(input_dto)
    return presenter.response


@doc(
    description="Marks the task with specified task_id active.",
    params={**auth_header_definition, **language_header_definition},
    tags=(tasks_blueprint.name,),
)
@marshal_with(ReactivateTaskSchema, http.HTTPStatus.OK)
@tasks_blueprint.route("/<uuid:task_id>/reactivate", methods=["PATCH"])
@jwt_required
def reactivate_task(
    task_id: TaskId,
    reactivate_task_uc: ReactivateTask,
    presenter: ReactivateTaskOutputBoundary,
    protector: TaskProtector,
) -> Response:
    input_dto: ReactivateTaskInputDto = get_dto_or_abort(ReactivateTaskSchema, {"id": task_id})

    protector.authorize(UUID(get_jwt_identity()), task_id)

    reactivate_task_uc.execute(input_dto)
    return presenter.response


@doc(
    description="Pins the task with specified task_id to the new project.",
    params={**auth_header_definition, **language_header_definition},
    tags=(tasks_blueprint.name,),
)
@marshal_with(PinTaskToProjectSchema, http.HTTPStatus.OK)
@use_kwargs(PinTaskToProjectSchema(exclude=("id",)))
@tasks_blueprint.route("/<uuid:task_id>/pin", methods=["PATCH"])
@jwt_required
def pin_task_to_project(
    task_id: TaskId,
    pin_task_to_project_uc: PinTaskToProject,
    presenter: PinTaskToProjectOutputBoundary,
    task_protector: TaskProtector,
    project_protector: ProjectProtector,
) -> Response:
    input_dto: PinTaskToProjectInputDto = get_dto_or_abort(PinTaskToProjectSchema, {"id": task_id})

    task_protector.authorize(UUID(get_jwt_identity()), task_id)
    project_protector.authorize(UUID(get_jwt_identity()), input_dto.new_project_id, abort_request=False)

    pin_task_to_project_uc.execute(input_dto)
    return presenter.response
