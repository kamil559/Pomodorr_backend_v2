from datetime import datetime
from typing import List, Type

from foundation.interfaces import Paginator
from foundation.utils import with_tzinfo
from foundation.value_objects import DateFrameDefinition, Priority, PriorityLevel
from pomodoros import GetTasksByProjectId, ProjectId, QueryTaskDto
from pomodoros.application.queries.tasks import GetRecentTasksByProjectId
from pomodoros.domain.entities import SubTask, Task
from pomodoros.domain.value_objects import TaskStatus
from pomodoros_infrastructure.models import TaskModel
from pony.orm import max as maximum
from pony.orm.core import Query  # noqa
from web_app.mixins import PaginatedQueryMixin, SortedQueryMixin


class SQLGetTasksByProjectId(SortedQueryMixin, PaginatedQueryMixin, GetTasksByProjectId):
    @staticmethod
    def _to_dto(task_model: Type[TaskModel]) -> QueryTaskDto:
        return QueryTaskDto(
            task_model.id,
            task_model.name,
            TaskStatus(task_model.status),
            task_model.project_id,
        )

    @staticmethod
    def _to_full_entity(task_model: Type[TaskModel]) -> Task:
        priority = Priority(task_model.priority_color, PriorityLevel(task_model.priority_level))
        date_frame_definition = DateFrameDefinition(
            task_model.pomodoro_length,
            task_model.break_length,
            task_model.longer_break_length,
            task_model.gap_between_long_breaks,
        )

        return Task(
            task_model.id,
            task_model.project_id,
            task_model.name,
            TaskStatus(task_model.status),
            priority,
            task_model.ordering,
            with_tzinfo(task_model.due_date),
            task_model.pomodoros_to_do,
            task_model.pomodoros_burn_down,
            date_frame_definition,
            with_tzinfo(task_model.reminder_date),
            task_model.renewal_interval,
            task_model.note,
            with_tzinfo(task_model.created_at),
            sub_tasks=list(
                map(
                    lambda sub_task: SubTask(
                        id=sub_task.id,
                        name=sub_task.name,
                        ordering=sub_task.ordering,
                        is_completed=sub_task.is_completed,
                    ),
                    task_model.sub_tasks,
                ),
            ),
        )

    @staticmethod
    def _apply_pagination(query: Query, paginator: Paginator):
        return query.page(paginator.page, paginator.page_size)

    def query(self, project_id: ProjectId, return_full_entity: bool = False) -> List[QueryTaskDto]:
        project_tasks = TaskModel.select(lambda task: task.project_id == project_id)

        project_tasks = self.get_paginated_query(self.get_sorted_query(project_tasks))

        if return_full_entity:
            return list(map(lambda task: self._to_full_entity(task), project_tasks))
        return list(map(lambda task: self._to_dto(task), project_tasks))


class SQLGetRecentTasksByProjectId(SortedQueryMixin, PaginatedQueryMixin, GetRecentTasksByProjectId):
    @staticmethod
    def _to_query_dto(task_model: Type[TaskModel]) -> QueryTaskDto:
        return QueryTaskDto(
            task_model.id,
            task_model.name,
            TaskStatus(task_model.status),
            task_model.project_id,
        )

    @staticmethod
    def _to_full_entity(task_model: Type[TaskModel]) -> Task:
        priority = Priority(task_model.priority_color, PriorityLevel(task_model.priority_level))
        date_frame_definition = DateFrameDefinition(
            task_model.pomodoro_length,
            task_model.break_length,
            task_model.longer_break_length,
            task_model.gap_between_long_breaks,
        )

        return Task(
            task_model.id,
            task_model.project_id,
            task_model.name,
            TaskStatus(task_model.status),
            priority,
            task_model.ordering,
            with_tzinfo(task_model.due_date),
            task_model.pomodoros_to_do,
            task_model.pomodoros_burn_down,
            date_frame_definition,
            with_tzinfo(task_model.reminder_date),
            task_model.renewal_interval,
            task_model.note,
            with_tzinfo(task_model.created_at),
            sub_tasks=list(
                map(
                    lambda sub_task: SubTask(
                        id=sub_task.id,
                        name=sub_task.name,
                        ordering=sub_task.ordering,
                        is_completed=sub_task.is_completed,
                    ),
                    task_model.sub_tasks,
                ),
            ),
        )

    @staticmethod
    def _is_from_most_recent_due_date(task_model: Type[TaskModel], most_recent_due_date: datetime) -> bool:
        return task_model.due_date.date() == most_recent_due_date.date()

    def query(self, project_id: ProjectId, return_full_entity: bool = False) -> List[QueryTaskDto]:
        most_recent_due_date = maximum(task.due_date for task in TaskModel if task.project_id == project_id)
        if not most_recent_due_date:
            return []

        recent_tasks = TaskModel.select(
            lambda task: task.project_id == project_id
            and self._is_from_most_recent_due_date(task, most_recent_due_date)
        )

        recent_tasks = self.get_paginated_query(self.get_sorted_query(recent_tasks))

        if return_full_entity:
            return list(map(lambda task: self._to_full_entity(task), recent_tasks))
        return list(map(lambda task: self._to_query_dto(task), recent_tasks))
