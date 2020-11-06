from typing import Type

from foundation.exceptions import AlreadyExists, NotFound
from foundation.utils import to_utc, with_tzinfo
from foundation.value_objects import DateFrameDefinition, Priority, PriorityLevel
from pomodoros import TaskId, TaskRepository
from pomodoros.domain.entities import SubTask, Task
from pomodoros.domain.value_objects import TaskStatus
from pomodoros_infrastructure import SubTaskModel
from pomodoros_infrastructure.models import TaskModel
from pony.orm import ObjectNotFound, delete


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
            id=task_model.id,
            project_id=task_model.project_id,
            name=task_model.name,
            status=TaskStatus(task_model.status),
            priority=priority,
            ordering=task_model.ordering,
            due_date=with_tzinfo(task_model.due_date),
            created_at=with_tzinfo(task_model.created_at),
            pomodoros_to_do=task_model.pomodoros_to_do,
            pomodoros_burn_down=task_model.pomodoros_burn_down,
            date_frame_definition=date_frame_definition,
            reminder_date=with_tzinfo(task_model.reminder_date),
            renewal_interval=task_model.renewal_interval,
            note=task_model.note,
            sub_tasks=list(
                map(
                    lambda sub_task: SubTask(
                        id=sub_task.id,
                        name=sub_task.name,
                        ordering=sub_task.ordering,
                        is_completed=sub_task.is_completed,
                    ),
                    task_model.sub_tasks,
                )
            ),
        )

    @staticmethod
    def _persist_sub_tasks(orm_task: Task, replace=False) -> None:
        if replace:
            delete(sub_task for sub_task in SubTaskModel if sub_task.task.id == orm_task.id)

        [
            SubTaskModel(
                id=sub_task.id,
                name=sub_task.name,
                task=orm_task,
                ordering=sub_task.ordering,
                is_completed=sub_task.is_completed,
            )
            for sub_task in orm_task.sub_tasks
        ]

    def _persist_new_orm_entity(self, task: Task) -> Type[TaskModel]:
        if TaskModel.exists(id=task.id):
            raise AlreadyExists()
        else:
            orm_task = TaskModel(
                id=task.id,
                project_id=task.project_id,
                name=task.name,
                status=task.status.value,
                priority_color=getattr(task.priority, "color", None),
                priority_level=getattr(task.priority.priority_level, "value", None),
                ordering=task.ordering,
                due_date=to_utc(task.due_date),
                pomodoros_to_do=task.pomodoros_to_do,
                pomodoros_burn_down=task.pomodoros_burn_down,
                reminder_date=to_utc(task.reminder_date),
                renewal_interval=task.renewal_interval,
                note=task.note,
                created_at=to_utc(task.created_at),
            )

            if task.date_frame_definition:
                orm_task.set(
                    **{
                        "pomodoro_length": getattr(task.date_frame_definition, "pomodoro_length", None),
                        "break_length": getattr(task.date_frame_definition, "break_length", None),
                        "longer_break_length": getattr(task.date_frame_definition, "longer_break_length", None),
                        "gap_between_long_breaks": getattr(task.date_frame_definition, "gap_between_long_breaks", None),
                    }
                )

            self._persist_sub_tasks(orm_task)

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
                "reminder_date": task.reminder_date,
                "renewal_interval": task.renewal_interval,
                "note": task.note,
            }

            if task.date_frame_definition:
                values_to_update.update(
                    {
                        "pomodoro_length": task.date_frame_definition.pomodoro_length,
                        "break_length": task.date_frame_definition.break_length,
                        "longer_break_length": task.date_frame_definition.longer_break_length,
                        "gap_between_long_breaks": task.date_frame_definition.gap_between_long_breaks,
                    }
                )

            orm_task = self._get_for_update(task.id)
            orm_task.set(**values_to_update)
            self._persist_sub_tasks(orm_task, replace=True)

    def delete(self, task_id: Task) -> None:
        TaskModel[task_id].delete()
