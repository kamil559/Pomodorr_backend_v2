import http
import uuid

from flask import abort
from foundation.interfaces import ResourceProtector
from foundation.value_objects import UserId
from pomodoros_infrastructure import ProjectModel
from pony.orm import select


class ProjectProtector(ResourceProtector):
    def authorize(self, requester_id: UserId, resource_id: uuid.UUID) -> None:
        project_id, owner_id = select(
            (project.id, project.owner_id) for project in ProjectModel if project.id == resource_id
        ).get()

        if project_id is None:
            abort(http.HTTPStatus.NOT_FOUND)

        if requester_id != owner_id:
            abort(http.HTTPStatus.FORBIDDEN)
