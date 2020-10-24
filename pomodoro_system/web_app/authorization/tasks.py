import uuid

from pony.orm import select
from werkzeug.exceptions import abort

from foundation.interfaces import ResourceProtector
from foundation.value_objects import UserId
from pomodoros_infrastructure import ProjectModel, TaskModel


class TaskProtector(ResourceProtector):
    def authorize(self, requester_id: UserId, resource_id: uuid.UUID) -> None:
        project_id = select(task.project_id for task in TaskModel if task.id == resource_id).get()
        owner_id = select(project.owner_id for project in ProjectModel if project.id == project_id).get()

        if requester_id != owner_id:
            abort(403)
