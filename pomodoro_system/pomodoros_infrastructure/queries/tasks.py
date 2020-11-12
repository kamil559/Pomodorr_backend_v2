from datetime import datetime
from typing import List, Type

from foundation.interfaces import Paginator
from pomodoros import GetTasksByProjectId, ProjectId, QueryTaskDto
from pomodoros.application.queries.tasks import GetRecentTasksByProjectId
from pomodoros.domain.entities import Task
from pomodoros.domain.value_objects import TaskStatus
from pomodoros_infrastructure.models import TaskModel
from pomodoros_infrastructure.repositories.tasks import SQLTaskRepository
from pony.orm import max as maximum
from pony.orm.core import Query  # noqa
from web_app.mixins import PaginatedQueryMixin, SortedQueryMixin


class SQLGetTasksByProjectId(SortedQueryMixin, PaginatedQueryMixin, GetTasksByProjectId):
    @staticmethod
    def _to_dto(orm_task: Type[TaskModel]) -> QueryTaskDto:
        return QueryTaskDto(
            id=orm_task.id,
            name=orm_task.name,
            status=TaskStatus(orm_task.status),
            project_id=orm_task.project.id,
        )

    @staticmethod
    def _to_full_entity(orm_task: Type[TaskModel]) -> Task:
        return SQLTaskRepository.to_domain_entity(orm_task)

    @staticmethod
    def _apply_pagination(query: Query, paginator: Paginator):
        return query.page(paginator.page, paginator.page_size)

    def query(self, project_id: ProjectId, return_full_entity: bool = False) -> List[QueryTaskDto]:
        project_tasks = TaskModel.select(lambda task: task.project.id == project_id)

        project_tasks = self.get_paginated_query(self.get_sorted_query(project_tasks))

        if return_full_entity:
            return list(map(lambda task: self._to_full_entity(task), project_tasks))
        return list(map(lambda task: self._to_dto(task), project_tasks))


class SQLGetRecentTasksByProjectId(SortedQueryMixin, PaginatedQueryMixin, GetRecentTasksByProjectId):
    @staticmethod
    def _to_query_dto(task_model: Type[TaskModel]) -> QueryTaskDto:
        return QueryTaskDto(
            id=task_model.id,
            name=task_model.name,
            status=TaskStatus(task_model.status),
            project_id=task_model.project.id,
        )

    @staticmethod
    def _to_full_entity(orm_task: Type[TaskModel]) -> Task:
        return SQLTaskRepository.to_domain_entity(orm_task)

    @staticmethod
    def _is_from_most_recent_due_date(orm_task: Type[TaskModel], most_recent_due_date: datetime) -> bool:
        return orm_task.due_date.date() == most_recent_due_date.date()

    def query(self, project_id: ProjectId, return_full_entity: bool = False) -> List[QueryTaskDto]:
        most_recent_due_date = maximum(task.due_date for task in TaskModel if task.project.id == project_id)
        if not most_recent_due_date:
            return []

        recent_tasks = TaskModel.select(
            lambda task: task.project.id == project_id
            and self._is_from_most_recent_due_date(task, most_recent_due_date)
        )

        recent_tasks = self.get_paginated_query(self.get_sorted_query(recent_tasks))

        if return_full_entity:
            return list(map(lambda task: self._to_full_entity(task), recent_tasks))
        return list(map(lambda task: self._to_query_dto(task), recent_tasks))
