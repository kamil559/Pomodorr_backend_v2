from datetime import datetime

import pytz
from flask import Blueprint, Response
from flask_jwt_extended import jwt_required, current_user, get_current_user

from pomodoros import (TaskId, BeginPomodoroOutputBoundary, BeginPomodoro, PomodoroId, PausePomodoro,
                       PausePomodoroOutputBoundary)
from serializers.pomodoros import BeginPomodoroSchema, PausePomodoroSchema
from web_app.authorization.pomodoros import BeginPomodoroResourceProtector, PausePomodoroResourceProtector
from web_app.utils import get_dto_or_abort

pomodoros_blueprint = Blueprint('pomodoros', __name__, url_prefix='/pomodoros')


@pomodoros_blueprint.route('/<uuid:task_id>/begin', methods=('POST',))
@jwt_required
def begin_pomodoro(task_id: TaskId, begin_pomodoro_uc: BeginPomodoro,
                   presenter: BeginPomodoroOutputBoundary, protector: BeginPomodoroResourceProtector) -> Response:
    input_dto = get_dto_or_abort(BeginPomodoroSchema, {'task_id': task_id,
                                                       'start_date': str(datetime.now(tz=pytz.UTC))})
    requester_id = current_user
    protector.authorize(requester_id, task_id)

    begin_pomodoro_uc.execute(input_dto)
    return presenter.response


@pomodoros_blueprint.route('/<uuid:pomodoro_id>/pause', methods=('PATCH',))
@jwt_required
def pause_pomodoro(pomodoro_id: PomodoroId, pause_pomodoro_uc: PausePomodoro,
                   presenter: PausePomodoroOutputBoundary, protector: PausePomodoroResourceProtector) -> Response:
    input_dto = get_dto_or_abort(PausePomodoroSchema, {'pomodoro_id': pomodoro_id,
                                                       'pause_date': str(datetime.now(tz=pytz.UTC))})
    requester_id = get_current_user()
    protector.authorize(requester_id, pomodoro_id)

    pause_pomodoro_uc.execute(input_dto)
    return presenter.response
