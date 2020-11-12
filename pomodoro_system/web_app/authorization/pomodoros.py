import http
import uuid
from gettext import gettext as _

from flask import abort
from foundation.exceptions import DomainValidationError
from foundation.interfaces import ResourceProtector
from foundation.value_objects import UserId
from pomodoros_infrastructure import PomodoroModel, TaskModel
from pony.orm import select


class PomodoroProtector(ResourceProtector):
    def authorize(self, requester_id: UserId, resource_id: uuid.UUID, abort_request: bool = True) -> None:
        task_id = select(pomodoro.task_id for pomodoro in PomodoroModel if pomodoro.id == resource_id).get() or None

        if task_id is None:
            raise DomainValidationError({"project_id": _("Selected task does not exist.")})

        project_id, owner_id = select(
            (task.project.id, task.project.owner_id) for task in TaskModel if task.id == task_id
        ).get() or (None, None)

        if project_id is None:
            raise DomainValidationError({"project_id": _("Selected project does not exist.")})

        if requester_id != owner_id:
            abort(http.HTTPStatus.FORBIDDEN)
