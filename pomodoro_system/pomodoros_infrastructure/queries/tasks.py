from datetime import datetime, timedelta
from enum import Enum
from typing import List, Type

from foundation.value_objects import UserId
from pomodoros import GetTaskListByOwnerId, ProjectId, QueryTaskDto
from pomodoros.application.queries.tasks import GetRecentTasksByProjectId
from pomodoros.domain.entities import Task
from pomodoros.domain.value_objects import TaskStatus
from pomodoros_infrastructure.models import TaskModel
from pomodoros_infrastructure.repositories.tasks import SQLTaskRepository
from pony.orm import max as maximum
from pony.orm.core import Query  # noqa
from web_app.mixins import FilteredQueryMixin, PaginatedQueryMixin, SortedQueryMixin


class SQLGetRecentTasksByProjectId(GetRecentTasksByProjectId):
    @staticmethod
    def _to_query_dto(task_model: Type[TaskModel]) -> QueryTaskDto:
        return QueryTaskDto(
            id=task_model.id,
            name=task_model.name,
            status=TaskStatus(task_model.status),
            project_id=task_model.project.id,
        )

    @staticmethod
    def _is_from_most_recent_due_date(due_date: datetime, most_recent_due_date: datetime) -> bool:
        return due_date.date() == most_recent_due_date.date()

    def query(self, project_id: ProjectId, return_full_entity: bool = False) -> List[QueryTaskDto]:
        most_recent_due_date = maximum(task.due_date for task in TaskModel if task.project.id == project_id)
        if not most_recent_due_date:
            return []

        recent_tasks = TaskModel.select(
            lambda task: task.project.id == project_id
            and task.is_active
            and self._is_from_most_recent_due_date(task.due_date, most_recent_due_date)
        )

        return list(map(lambda task: self._to_query_dto(task), recent_tasks))


class DueDateFilter(Enum):
    RECENT = 0
    TODAY = 1
    TOMORROW = 2
    UPCOMING = 3


class SQLGetTaskListByOwnerId(FilteredQueryMixin, PaginatedQueryMixin, SortedQueryMixin, GetTaskListByOwnerId):
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
    def _is_owner(task_owner_id: UserId, current_user_id: UserId) -> bool:
        return task_owner_id == current_user_id

    def _get_basic_task_list(self, owner_id: UserId) -> Query:
        return TaskModel.select(lambda task: self._is_owner(task.project.owner.id, owner_id))

    def _get_recent_task_list(self, owner_id: UserId) -> Query:
        today = datetime.utcnow()
        most_recent_due_date = maximum(
            task.due_date
            for task in TaskModel
            if self._is_owner(task.project.owner.id, owner_id) and task.due_date.date() <= today.date()
        )

        if not most_recent_due_date:
            return []

        return TaskModel.select(
            lambda task: self._is_owner(task.project.owner.id, owner_id)
            and task.due_date.date() == most_recent_due_date.date()
        )

    def _get_task_list_for_today(self, owner_id: UserId) -> Query:
        today = datetime.utcnow()
        return TaskModel.select(
            lambda task: self._is_owner(task.project.owner.id, owner_id) and task.due_date.date() == today.date()
        )

    def _get_task_list_for_tomorrow(self, owner_id: UserId) -> Query:
        tomorrow = datetime.utcnow() + timedelta(days=1)
        return TaskModel.select(
            lambda task: self._is_owner(task.project.owner.id, owner_id) and task.due_date.date() == tomorrow.date()
        )

    def _get_upcoming_task_list(self, owner_id: UserId) -> Query:
        tomorrow = datetime.utcnow() + timedelta(days=1)
        return TaskModel.select(
            lambda task: self._is_owner(task.project.owner.id, owner_id) and task.due_date.date() > tomorrow.date()
        )

    def _get_task_list_for_due_date(self, owner_id: UserId, rule: DueDateFilter) -> Query:
        task_query = None

        if rule is DueDateFilter(DueDateFilter.RECENT):
            task_query = self._get_recent_task_list(owner_id)
        elif rule is DueDateFilter(DueDateFilter.TODAY):
            task_query = self._get_task_list_for_today(owner_id)
        elif rule is DueDateFilter(DueDateFilter.TOMORROW):
            task_query = self._get_task_list_for_tomorrow(owner_id)
        elif rule is DueDateFilter(DueDateFilter.UPCOMING):
            task_query = self._get_upcoming_task_list(owner_id)

        return task_query

    def query(self, owner_id: UserId, return_full_entity: bool = False, **kwargs) -> List[QueryTaskDto]:
        filter_fields: dict = kwargs.get("filter_fields", {}) or {}
        due_date_rule = filter_fields.pop("due_date_rule", None)

        if due_date_rule is None:
            task_query = self._get_basic_task_list(owner_id=owner_id)
        else:
            task_query = self._get_task_list_for_due_date(owner_id=owner_id, rule=due_date_rule)

        task_query = self.get_paginated_query(self.get_sorted_query(self.get_filtered_query(task_query, filter_fields)))

        if return_full_entity:
            return list(map(lambda task: self._to_full_entity(task), task_query))
        return list(map(lambda task: self._to_dto(task), task_query))
