from typing import Type

from foundation.exceptions import AlreadyExists, NotFound
from foundation.utils import to_utc, with_tzinfo
from foundation.value_objects import (DateFrameDefinition, Priority,
                                      PriorityLevel)
from pomodoros import TaskId, TaskRepository
from pomodoros.domain.entities import SubTask, Task
from pomodoros.domain.value_objects import TaskStatus
from pomodoros_infrastructure import SubTaskModel
from pomodoros_infrastructure.models import TaskModel
from pony.orm import ObjectNotFound


class SQLTaskRepository(TaskRepository):
    @staticmethod
    def _to_entity(task_model: Type[TaskModel]) -> Task:
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
                        sub_task.id,
                        sub_task.name,
                        sub_task.id,
                        with_tzinfo(sub_task.created_at),
                        sub_task.is_completed,
                    ),
                    task_model.sub_tasks,
                )
            ),
        )

    @staticmethod
    def _persist_new_orm_entity(task: Task) -> Type[TaskModel]:
        if TaskModel.exists(id=task.id):
            raise AlreadyExists()
        else:
            orm_task = TaskModel(
                id=task.id,
                project_id=task.project_id,
                name=task.name,
                status=task.status.value,
                priority_color=task.priority.color,
                priority_level=task.priority.priority_level.value,
                ordering=task.ordering,
                due_date=to_utc(task.due_date),
                pomodoros_to_do=task.pomodoros_to_do,
                pomodoros_burn_down=task.pomodoros_burn_down,
                pomodoro_length=task.date_frame_definition.pomodoro_length,
                break_length=task.date_frame_definition.break_length,
                longer_break_length=task.date_frame_definition.longer_break_length,
                gap_between_long_breaks=task.date_frame_definition.gap_between_long_breaks,
                reminder_date=to_utc(task.reminder_date),
                renewal_interval=task.renewal_interval,
                note=task.note,
                created_at=to_utc(task.created_at),
            )
            [
                SubTaskModel(
                    id=sub_task.id,
                    name=sub_task.name,
                    task=orm_task,
                    created_at=to_utc(sub_task.created_at),
                    is_completed=sub_task.is_completed,
                )
                for sub_task in task.sub_tasks
            ]

    def get(self, task_id: TaskId) -> Task:
        try:
            task = TaskModel[task_id]
        except ObjectNotFound:
            raise NotFound()
        else:
            return self._to_entity(task)

    @staticmethod
    def _get_for_update(task_id: TaskId) -> Type[TaskModel]:
        orm_task = TaskModel.get_for_update(id=task_id)

        if orm_task is None:
            raise NotFound()
        return orm_task

    def save(self, task: Task, create: bool = False) -> None:
        if create:
            self._persist_new_orm_entity(task)
        else:
            values_to_update = {
                "project_id": task.project_id,
                "name": task.name,
                "status": task.status.value,
                "priority_color": task.priority.color,
                "priority_level": task.priority.priority_level.value,
                "ordering": task.ordering,
                "due_date": task.due_date,
                "pomodoros_to_do": task.pomodoros_to_do,
                "pomodoros_burn_down": task.pomodoros_burn_down,
                "pomodoro_length": task.date_frame_definition.pomodoro_length,
                "break_length": task.date_frame_definition.break_length,
                "longer_break_length": task.date_frame_definition.longer_break_length,
                "gap_between_long_breaks": task.date_frame_definition.gap_between_long_breaks,
                "reminder_date": task.reminder_date,
                "renewal_interval": task.renewal_interval,
                "note": task.note,
            }

            task = self._get_for_update(task.id)
            task.set(**values_to_update)
