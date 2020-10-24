from typing import List, Optional

from pomodoros.application.queries.tasks import GetTasksByProjectId, TaskDto
from pomodoros.domain.entities import Task
from pomodoros.domain.value_objects import ProjectId


class GetTasksByProjectIdStub(GetTasksByProjectId):
    def __init__(self, return_collection: Optional[List[Task]] = None):
        if return_collection is not None:
            self._rows = return_collection
        else:
            self._rows = []

    @staticmethod
    def _to_task_dto(task: Task) -> TaskDto:
        return TaskDto(task.id, task.name, task.status, task.project_id)

    def query(self, project_id: ProjectId) -> Optional[List[TaskDto]]:
        return list(
            map(
                lambda task: self._to_task_dto(task),
                filter(lambda row: row.project_id == project_id, self._rows),
            )
        )
