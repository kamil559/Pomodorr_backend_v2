import uuid

from flask import abort
from foundation.interfaces import ResourceProtector
from foundation.value_objects import UserId
from pomodoros_infrastructure import PomodoroModel, ProjectModel, TaskModel
from pony.orm import select


class PomodoroProtector(ResourceProtector):
    def authorize(self, requester_id: UserId, resource_id: uuid.UUID) -> None:
        task_id_query = select(pomodoro.task_id for pomodoro in PomodoroModel if pomodoro.id == resource_id)
        project_id_query = select(task.project_id for task in TaskModel if task.id == task_id_query.get())
        owner_id = select(project.owner_id for project in ProjectModel if project.id == project_id_query.get()).get()

        if requester_id != owner_id:
            abort(403)
