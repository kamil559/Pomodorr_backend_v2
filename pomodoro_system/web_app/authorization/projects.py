import uuid

from flask import abort
from pony.orm import select

from foundation.interfaces import ResourceProtector
from foundation.value_objects import UserId
from pomodoros_infrastructure import ProjectModel


class ProjectProtector(ResourceProtector):
    def authorize(self, requester_id: UserId, resource_id: uuid.UUID) -> None:
        owner_id = select(project.owner_id for project in ProjectModel if project.id == resource_id).get()

        if requester_id != owner_id:
            abort(403)
