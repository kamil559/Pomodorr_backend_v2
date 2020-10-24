import uuid

from pony.orm import select
from werkzeug.exceptions import abort

from interfaces import ResourceProtector
from pomodoros_infrastructure import ProjectModel, TaskModel
from value_objects import UserId


class TaskProtector(ResourceProtector):
    def authorize(self, requester_id: UserId, resource_id: uuid.UUID) -> None:
        project_id = select(task.project_id for task in TaskModel if task.id == resource_id).get()
        owner_id = select(project.owner_id for project in ProjectModel if project.id == project_id).get()

        if requester_id != owner_id:
            abort(403)
