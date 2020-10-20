from datetime import datetime

import pytz
from flask import Blueprint, Response

from pomodoros import (TaskId, BeginPomodoroOutputBoundary, BeginPomodoro)
from serializers.pomodoros import BeginPomodoroSchema
from web_app.utils import get_dto_or_abort

pomodoros_blueprint = Blueprint('pomodoros', __name__, url_prefix='/pomodoros')


@pomodoros_blueprint.route('/<uuid:task_id>/begin', methods=('POST',))
def begin_pomodoro(task_id: TaskId, begin_pomodoro_uc: BeginPomodoro,
                   presenter: BeginPomodoroOutputBoundary) -> Response:
    input_dto = get_dto_or_abort(BeginPomodoroSchema, {'task_id': task_id,
                                                       'start_date': str(datetime.now(tz=pytz.UTC))})

    begin_pomodoro_uc.execute(input_dto)

    return presenter.response
