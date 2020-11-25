import http
import uuid

from flask import abort
from foundation.exceptions import DomainValidationError
from foundation.i18n import N_
from foundation.interfaces import ResourceProtector
from foundation.value_objects import UserId
from pomodoros_infrastructure import TaskModel
from pony.orm import select


class TaskProtector(ResourceProtector):
    def authorize(self, requester_id: UserId, resource_id: uuid.UUID, abort_request: bool = True) -> None:
        task_id, owner_id = select(
            (task.id, task.project.owner.id) for task in TaskModel if task.id == resource_id
        ).get() or (None, None)

        if task_id is None:
            if abort_request:
                abort(http.HTTPStatus.NOT_FOUND)
            else:
                raise DomainValidationError({"task_id": N_("Selected task does not exist.")})

        if requester_id != owner_id:
            abort(http.HTTPStatus.FORBIDDEN)
