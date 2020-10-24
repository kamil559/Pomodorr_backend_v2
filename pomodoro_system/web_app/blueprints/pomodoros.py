from datetime import datetime

import pytz
from flask import Blueprint, Response
from flask_jwt_extended import get_current_user, jwt_required

from authorization.tasks import TaskProtector
from pomodoros import (
    BeginPomodoro,
    BeginPomodoroInputDto,
    BeginPomodoroOutputBoundary,
    FinishPomodoro,
    FinishPomodoroInputDto,
    FinishPomodoroOutputBoundary,
    PausePomodoro,
    PausePomodoroInputDto,
    PausePomodoroOutputBoundary,
    PomodoroId,
    ResumePomodoro,
    ResumePomodoroInputDto,
    ResumePomodoroOutputBoundary,
    TaskId,
)
from serializers.pomodoros import BeginPomodoroSchema, FinishPomodoroSchema, PausePomodoroSchema, ResumePomodoroSchema
from web_app.authorization.pomodoros import PomodoroProtector
from web_app.utils import get_dto_or_abort

pomodoros_blueprint = Blueprint("pomodoros", __name__, url_prefix="/pomodoros")


@pomodoros_blueprint.route("/<uuid:task_id>/begin", methods=["POST"])
@jwt_required
def begin_pomodoro(
        task_id: TaskId,
        begin_pomodoro_uc: BeginPomodoro,
        presenter: BeginPomodoroOutputBoundary,
        protector: TaskProtector,
) -> Response:
    input_dto: BeginPomodoroInputDto = get_dto_or_abort(
        BeginPomodoroSchema,
        {"task_id": task_id, "start_date": str(datetime.now(tz=pytz.UTC))},
    )
    requester_id = get_current_user()
    protector.authorize(requester_id, task_id)

    begin_pomodoro_uc.execute(input_dto)
    return presenter.response


@pomodoros_blueprint.route("/<uuid:pomodoro_id>/pause", methods=["POST"])
@jwt_required
def pause_pomodoro(
        pomodoro_id: PomodoroId,
        pause_pomodoro_uc: PausePomodoro,
        presenter: PausePomodoroOutputBoundary,
        protector: PomodoroProtector,
) -> Response:
    input_dto: PausePomodoroInputDto = get_dto_or_abort(
        PausePomodoroSchema,
        {"pomodoro_id": pomodoro_id, "pause_date": str(datetime.now(tz=pytz.UTC))},
    )
    requester_id = get_current_user()
    protector.authorize(requester_id, pomodoro_id)

    pause_pomodoro_uc.execute(input_dto)
    return presenter.response


@pomodoros_blueprint.route("/<uuid:pomodoro_id>/resume", methods=["POST"])
@jwt_required
def resume_pomodoro(
        pomodoro_id: PomodoroId,
        resume_pomodoro_uc: ResumePomodoro,
        presenter: ResumePomodoroOutputBoundary,
        protector: PomodoroProtector,
) -> Response:
    input_dto: ResumePomodoroInputDto = get_dto_or_abort(
        ResumePomodoroSchema,
        {"pomodoro_id": pomodoro_id, "resume_date": str(datetime.now(tz=pytz.UTC))},
    )
    requester_id = get_current_user()
    protector.authorize(requester_id, pomodoro_id)

    resume_pomodoro_uc.execute(input_dto)
    return presenter.response


@pomodoros_blueprint.route("/<uuid:pomodoro_id>/finish", methods=["PATCH"])
@jwt_required
def finish_pomodoro(
        pomodoro_id: PomodoroId,
        finish_pomodoro_uc: FinishPomodoro,
        presenter: FinishPomodoroOutputBoundary,
        protector: PomodoroProtector,
) -> Response:
    requester_id = get_current_user()
    input_dto: FinishPomodoroInputDto = get_dto_or_abort(
        FinishPomodoroSchema,
        {
            "id": pomodoro_id,
            "end_date": str(datetime.now(tz=pytz.UTC)),
            "owner_id": requester_id,
        },
    )

    protector.authorize(requester_id, pomodoro_id)

    finish_pomodoro_uc.execute(input_dto)
    return presenter.response
