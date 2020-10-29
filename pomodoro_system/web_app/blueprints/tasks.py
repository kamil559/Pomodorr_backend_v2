from datetime import datetime

import pytz
from flask import Response
from flask_apispec import doc, marshal_with, use_kwargs
from flask_login import current_user
from flask_security import auth_token_required
from pomodoros import (
    CompleteTask,
    CompleteTaskInputDto,
    CompleteTaskOutputBoundary,
    PinTaskToProject,
    PinTaskToProjectInputDto,
    PinTaskToProjectOutputBoundary,
    ReactivateTask,
    ReactivateTaskInputDto,
    ReactivateTaskOutputBoundary,
    TaskId,
)
from web_app.authorization.projects import ProjectProtector
from web_app.authorization.tasks import TaskProtector
from web_app.serializers.tasks import CompleteTaskSchema, PinTaskToProjectSchema, ReactivateTaskSchema
from web_app.utils import RegistrableBlueprint, get_dto_or_abort
from webargs import fields

tasks_blueprint = RegistrableBlueprint("tasks", __name__, url_prefix="/tasks")


@doc(
    description="Takes the task id (UUID string) and marks it as completed.",
    params={"Authorization": {"in": "header", "type": "string", "required": True}},
    tags=("tasks",),
)
@marshal_with(CompleteTaskSchema, 200, description="{new_task_id} is returned only if a repeatable task was completed.")
@tasks_blueprint.route("/<uuid:task_id>/complete", methods=["PATCH"])
@auth_token_required
def complete_task(
    task_id: TaskId,
    complete_task_uc: CompleteTask,
    presenter: CompleteTaskOutputBoundary,
    protector: TaskProtector,
) -> Response:
    input_dto: CompleteTaskInputDto = get_dto_or_abort(
        CompleteTaskSchema,
        {"id": task_id, "completed_at": str(datetime.now(tz=pytz.UTC))},
    )

    protector.authorize(current_user.id, task_id)

    complete_task_uc.execute(input_dto)
    return presenter.response


@doc(
    description="Takes the task id (UUID string) and marks it as active.",
    params={"Authorization": {"in": "header", "type": "string", "required": True}},
    tags=("tasks",),
)
@marshal_with(ReactivateTaskSchema, 200)
@tasks_blueprint.route("/<uuid:task_id>/reactivate", methods=["PATCH"])
@auth_token_required
def reactivate_task(
    task_id: TaskId,
    reactivate_task_uc: ReactivateTask,
    presenter: ReactivateTaskOutputBoundary,
    protector: TaskProtector,
) -> Response:
    input_dto: ReactivateTaskInputDto = get_dto_or_abort(ReactivateTaskSchema, {"id": task_id})

    protector.authorize(current_user.id, task_id)

    reactivate_task_uc.execute(input_dto)
    return presenter.response


@doc(
    description="Takes the task id (UUID string) pins it to the new project.",
    params={"Authorization": {"in": "header", "type": "string", "required": True}},
    tags=("tasks",),
)
@marshal_with(PinTaskToProjectSchema, 200)
@use_kwargs({"new_project_id": fields.UUID(required=True)})
@tasks_blueprint.route("/<uuid:task_id>/pin", methods=["PATCH"])
@auth_token_required
def pin_task_to_project(
    task_id: TaskId,
    pin_task_to_project_uc: PinTaskToProject,
    presenter: PinTaskToProjectOutputBoundary,
    task_protector: TaskProtector,
    project_protector: ProjectProtector,
) -> Response:
    input_dto: PinTaskToProjectInputDto = get_dto_or_abort(PinTaskToProjectSchema, {"id": task_id})

    task_protector.authorize(current_user.id, task_id)
    project_protector.authorize(current_user.id, input_dto.new_project_id)

    pin_task_to_project_uc.execute(input_dto)
    return presenter.response
