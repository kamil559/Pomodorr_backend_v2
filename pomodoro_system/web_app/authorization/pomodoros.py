import http
import uuid

from flask import abort
from foundation.exceptions import DomainValidationError
from foundation.i18n import N_
from foundation.interfaces import ResourceProtector
from foundation.value_objects import UserId
from pomodoros_infrastructure import PomodoroModel
from pony.orm import select


class PomodoroProtector(ResourceProtector):
    def authorize(self, requester_id: UserId, resource_id: uuid.UUID, abort_request: bool = True) -> None:
        pomodoro_id, owner_id = select(
            (pomodoro.id, pomodoro.task.project.owner.id) for pomodoro in PomodoroModel if pomodoro.id == resource_id
        ).get() or (None, None)

        if pomodoro_id is None:
            if abort_request:
                abort(http.HTTPStatus.NOT_FOUND)
            else:
                raise DomainValidationError({"pomodoro_id": N_("Selected pomodoro does not exist.")})

        if requester_id != owner_id:
            abort(http.HTTPStatus.FORBIDDEN)
