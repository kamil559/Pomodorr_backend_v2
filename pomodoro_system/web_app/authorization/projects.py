import http
import uuid
from gettext import gettext as _

from flask import abort
from foundation.exceptions import DomainValidationError
from foundation.interfaces import ResourceProtector
from foundation.value_objects import UserId
from pomodoros_infrastructure import ProjectModel
from pony.orm import select


class ProjectProtector(ResourceProtector):
    def authorize(self, requester_id: UserId, resource_id: uuid.UUID, abort_request: bool = True) -> None:
        project_id, owner_id = select(
            (project.id, project.owner_id)
            for project in ProjectModel
            if project.id == resource_id and project.deleted_at is None
        ).get() or (None, None)

        if project_id is None:
            if abort_request:
                abort(http.HTTPStatus.NOT_FOUND)
            else:
                raise DomainValidationError({"project_id": _("Selected project does not exist.")})

        if requester_id != owner_id:
            abort(http.HTTPStatus.FORBIDDEN)
