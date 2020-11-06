import http
import uuid

from foundation.interfaces import ResourceProtector
from foundation.value_objects import UserId
from pomodoros_infrastructure import ProjectModel, TaskModel
from pony.orm import select
from werkzeug.exceptions import abort


class TaskProtector(ResourceProtector):
    def authorize(self, requester_id: UserId, resource_id: uuid.UUID) -> None:
        task_id, project_id = select((task.id, task.project_id) for task in TaskModel if task.id == resource_id).get()

        if task_id is None:
            abort(http.HTTPStatus.NOT_FOUND)

        owner_id = select(project.owner_id for project in ProjectModel if project.id == project_id).get()

        if requester_id != owner_id:
            abort(http.HTTPStatus.FORBIDDEN)
