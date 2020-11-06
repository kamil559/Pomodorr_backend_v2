from datetime import datetime
from typing import List, Optional

from foundation.interfaces import Paginator
from pomodoros.application.queries.tasks import GetRecentTasksByProjectId, QueryTaskDto
from pomodoros.domain.entities import Task
from pomodoros.domain.value_objects import ProjectId


class GetRecentTasksByProjectIdStub(GetRecentTasksByProjectId):
    def __init__(self, return_collection: Optional[List[Task]] = None):
        if return_collection is not None:
            self._rows = return_collection
        else:
            self._rows = []

    @staticmethod
    def _to_task_dto(task: Task) -> QueryTaskDto:
        return QueryTaskDto(task.id, task.name, task.status, task.project_id)

    @staticmethod
    def _is_from_most_recent_due_date(task: Task, most_recent_date: datetime) -> bool:
        return task.created_at.date() == most_recent_date.date()

    def query(
        self, project_id: ProjectId, paginator: Paginator = None, return_full_entity: bool = False
    ) -> Optional[List[QueryTaskDto]]:
        most_recent_due_date = max([task.created_at for task in self._rows])

        if not most_recent_due_date:
            return []

        recent_tasks = list(
            map(
                lambda task: self._to_task_dto(task),
                filter(
                    lambda row: row.project_id == project_id
                    and self._is_from_most_recent_due_date(row, most_recent_due_date),
                    self._rows,
                ),
            )
        )

        return recent_tasks
