from datetime import datetime

import pytz
from flask import Blueprint, Response
from flask_jwt_extended import jwt_required, get_current_user

from authorization.tasks import TaskProtector
from pomodoros import TaskId, CompleteTask, CompleteTaskOutputBoundary
from serializers.tasks import CompleteTaskSchema
from web_app.utils import get_dto_or_abort

tasks_blueprint = Blueprint('tasks', __name__, url_prefix='/tasks')


@tasks_blueprint.route('/<uuid:task_id>/complete', methods=['PATCH'])
@jwt_required
def complete_task(task_id: TaskId, complete_task_uc: CompleteTask, presenter: CompleteTaskOutputBoundary,
                  protector: TaskProtector) -> Response:
    input_dto = get_dto_or_abort(CompleteTaskSchema, {'id': task_id, 'completed_at': str(datetime.now(tz=pytz.UTC))})

    requester_id = get_current_user()
    protector.authorize(requester_id, task_id)

    complete_task_uc.execute(input_dto)
    return presenter.response
