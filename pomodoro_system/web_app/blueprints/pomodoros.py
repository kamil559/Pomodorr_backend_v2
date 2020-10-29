from datetime import datetime

import pytz
from flask import Response
from flask_apispec import doc, marshal_with
from flask_login import current_user
from flask_security import auth_token_required
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
from web_app.authorization.pomodoros import PomodoroProtector
from web_app.authorization.tasks import TaskProtector
from web_app.serializers.pomodoros import (
    BeginPomodoroSchema,
    FinishPomodoroSchema,
    PausePomodoroSchema,
    ResumePomodoroSchema,
)
from web_app.utils import RegistrableBlueprint, get_dto_or_abort

pomodoros_blueprint = RegistrableBlueprint("pomodoros", __name__, url_prefix="/pomodoros")


@doc(
    description="Takes the task id (UUID string) and starts a pomodoro upon the task.",
    params={"Authorization": {"in": "header", "type": "string", "required": True}},
    tags=("pomodoros",),
)
@marshal_with(BeginPomodoroSchema, 201)
@pomodoros_blueprint.route("/<uuid:task_id>/begin", methods=["POST"])
@auth_token_required
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
    protector.authorize(current_user.id, task_id)

    begin_pomodoro_uc.execute(input_dto)
    return presenter.response


@doc(
    description="Takes the current pomodoro's id (UUID string) and pauses it.",
    params={"Authorization": {"in": "header", "type": "string", "required": True}},
    tags=("pomodoros",),
)
@marshal_with(PausePomodoroSchema, 200)
@pomodoros_blueprint.route("/<uuid:pomodoro_id>/pause", methods=["POST"])
@auth_token_required
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
    protector.authorize(current_user.id, pomodoro_id)

    pause_pomodoro_uc.execute(input_dto)
    return presenter.response


@doc(
    description="Takes the paused pomodoro's id (UUID string) and resumes it.",
    params={"Authorization": {"in": "header", "type": "string", "required": True}},
    tags=("pomodoros",),
)
@marshal_with(ResumePomodoroSchema, 200)
@pomodoros_blueprint.route("/<uuid:pomodoro_id>/resume", methods=["POST"])
@auth_token_required
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
    protector.authorize(current_user.id, pomodoro_id)

    resume_pomodoro_uc.execute(input_dto)
    return presenter.response


@doc(
    description="Takes the current pomodoro's id (UUID string) and finishes it.",
    params={"Authorization": {"in": "header", "type": "string", "required": True}},
    tags=("pomodoros",),
)
@marshal_with(FinishPomodoroSchema(exclude=("owner_id",)), 200)
@pomodoros_blueprint.route("/<uuid:pomodoro_id>/finish", methods=["PATCH"])
@auth_token_required
def finish_pomodoro(
    pomodoro_id: PomodoroId,
    finish_pomodoro_uc: FinishPomodoro,
    presenter: FinishPomodoroOutputBoundary,
    protector: PomodoroProtector,
) -> Response:
    input_dto: FinishPomodoroInputDto = get_dto_or_abort(
        FinishPomodoroSchema,
        {
            "id": pomodoro_id,
            "end_date": str(datetime.now(tz=pytz.UTC)),
            "owner_id": current_user.id,
        },
    )
    protector.authorize(current_user.id, pomodoro_id)

    finish_pomodoro_uc.execute(input_dto)
    return presenter.response
