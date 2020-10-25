from datetime import datetime

import pytz
from flask import Blueprint, Response
from flask_jwt_extended import get_current_user, jwt_required
from pomodoros import (CompleteTask, CompleteTaskInputDto,
                       CompleteTaskOutputBoundary, PinTaskToProject,
                       PinTaskToProjectInputDto,
                       PinTaskToProjectOutputBoundary, ReactivateTask,
                       ReactivateTaskInputDto, ReactivateTaskOutputBoundary,
                       TaskId)
from web_app.authorization.projects import ProjectProtector
from web_app.authorization.tasks import TaskProtector
from web_app.serializers.tasks import (CompleteTaskSchema,
                                       PinTaskToProjectSchema,
                                       ReactivateTaskSchema)
from web_app.utils import get_dto_or_abort

tasks_blueprint = Blueprint("tasks", __name__, url_prefix="/tasks")


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
        {"id": task_id, "completed_at": str(datetime.now(tz=pytz.UTC))},
    )

    requester_id = get_current_user()
    protector.authorize(requester_id, task_id)

    complete_task_uc.execute(input_dto)
    return presenter.response


@tasks_blueprint.route("/<uuid:task_id>/reactivate", methods=["PATCH"])
@jwt_required
def reactivate_task(
    task_id: TaskId,
    reactivate_task_uc: ReactivateTask,
    presenter: ReactivateTaskOutputBoundary,
    protector: TaskProtector,
) -> Response:
    input_dto: ReactivateTaskInputDto = get_dto_or_abort(ReactivateTaskSchema, {"id": task_id})

    requester_id = get_current_user()
    protector.authorize(requester_id, task_id)

    reactivate_task_uc.execute(input_dto)
    return presenter.response


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

    requester_id = get_current_user()
    task_protector.authorize(requester_id, task_id)
    project_protector.authorize(requester_id, input_dto.new_project_id)

    pin_task_to_project_uc.execute(input_dto)
    return presenter.response
