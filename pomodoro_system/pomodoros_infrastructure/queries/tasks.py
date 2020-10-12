from typing import Optional, List, Type

from pomodoros import GetTasksByProjectId, ProjectId, TaskDto
from pomodoros.domain.value_objects import TaskStatus
from pomodoros_infrastructure.models import Task as TaskModel


class SQLGetTasksByProjectId(GetTasksByProjectId):
    @staticmethod
    def _to_dto(task_model: Type[TaskModel]) -> TaskDto:
        return TaskDto(task_model.id, task_model.name, TaskStatus(task_model.status), task_model.project_id)

    def query(self, project_id: ProjectId) -> Optional[List[TaskDto]]:
        project_tasks = TaskModel.select(lambda task: task.project_id == project_id)
        if project_tasks:
            return list(map(lambda task: self._to_dto(task), project_tasks))
