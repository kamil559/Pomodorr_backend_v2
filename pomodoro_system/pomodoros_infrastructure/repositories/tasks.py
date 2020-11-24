from gettext import gettext as _
from typing import Optional, Type

from foundation.exceptions import AlreadyExists, NotFound
from foundation.utils import to_utc, with_tzinfo
from foundation.value_objects import Color, DateFrameDefinition, Priority, PriorityLevel
from pomodoros import TaskId, TaskRepository
from pomodoros.domain.entities import SubTask, Task
from pomodoros.domain.value_objects import TaskStatus
from pomodoros_infrastructure import SubTaskModel
from pomodoros_infrastructure.models import TaskModel
from pony.orm import ObjectNotFound, delete


class SQLTaskRepository(TaskRepository):
    @classmethod
    def to_domain_entity(cls, orm_task: Type[TaskModel]) -> Task:
        priority = Priority(
            color=Color(hex=orm_task.priority_color), priority_level=PriorityLevel(orm_task.priority_level)
        )
        date_frame_definition = DateFrameDefinition(
            pomodoro_length=orm_task.pomodoro_length,
            break_length=orm_task.break_length,
            longer_break_length=orm_task.longer_break_length,
            gap_between_long_breaks=orm_task.gap_between_long_breaks,
        )

        return Task(
            id=orm_task.id,
            project_id=orm_task.project.id,
            name=orm_task.name,
            status=TaskStatus(orm_task.status),
            priority=priority,
            ordering=orm_task.ordering,
            due_date=with_tzinfo(orm_task.due_date),
            created_at=with_tzinfo(orm_task.created_at),
            pomodoros_to_do=orm_task.pomodoros_to_do,
            pomodoros_burn_down=orm_task.pomodoros_burn_down,
            date_frame_definition=date_frame_definition,
            reminder_date=with_tzinfo(orm_task.reminder_date),
            renewal_interval=orm_task.renewal_interval,
            note=orm_task.note,
            sub_tasks=list(
                map(
                    lambda sub_task: SubTask(
                        id=sub_task.id,
                        name=sub_task.name,
                        ordering=sub_task.ordering,
                        is_completed=with_tzinfo(sub_task.is_completed),
                    ),
                    orm_task.sub_tasks,
                )
            ),
        )

    @staticmethod
    def _persist_sub_tasks(orm_task: Task, replace: bool = False) -> None:
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

    def _persist_new_orm_task(self, task_entity: Task) -> None:
        if TaskModel.exists(project=task_entity.project_id, name=task_entity.name):
            raise AlreadyExists(
                {
                    "name": [
                        _("Task with name '{name}' already exists within the project.").format(name=task_entity.name)
                    ]
                }
            )
        else:
            priority = task_entity.priority

            orm_task = TaskModel(
                id=task_entity.id,
                project=task_entity.project_id,
                name=task_entity.name,
                status=task_entity.status.value,
                priority_color=getattr(priority.color, "hex", None),
                priority_level=getattr(priority.priority_level, "value", None),
                ordering=task_entity.ordering,
                due_date=to_utc(task_entity.due_date),
                pomodoros_to_do=task_entity.pomodoros_to_do,
                pomodoros_burn_down=task_entity.pomodoros_burn_down,
                reminder_date=to_utc(task_entity.reminder_date),
                renewal_interval=task_entity.renewal_interval,
                note=task_entity.note,
                created_at=to_utc(task_entity.created_at),
            )

            date_frame_definition = task_entity.date_frame_definition
            orm_task.set(
                **{
                    "pomodoro_length": getattr(date_frame_definition, "pomodoro_length", None),
                    "break_length": getattr(date_frame_definition, "break_length", None),
                    "longer_break_length": getattr(date_frame_definition, "longer_break_length", None),
                    "gap_between_long_breaks": getattr(date_frame_definition, "gap_between_long_breaks", None),
                }
            )

            self._persist_sub_tasks(orm_task)

    @staticmethod
    def _get_for_update(task_id: TaskId) -> Optional[Type[TaskModel]]:
        return TaskModel.get_for_update(id=task_id)

    def _update_existing_orm_task(self, task_entity: Task) -> None:
        values_to_update = {
            "project": task_entity.project_id,
            "name": task_entity.name,
            "status": task_entity.status.value,
            "priority_color": task_entity.priority.color.hex,
            "priority_level": task_entity.priority.priority_level.value,
            "ordering": task_entity.ordering,
            "due_date": task_entity.due_date,
            "pomodoros_to_do": task_entity.pomodoros_to_do,
            "reminder_date": task_entity.reminder_date,
            "renewal_interval": task_entity.renewal_interval,
            "note": task_entity.note,
        }

        if task_entity.date_frame_definition:
            values_to_update.update(
                {
                    "pomodoro_length": task_entity.date_frame_definition.pomodoro_length,
                    "break_length": task_entity.date_frame_definition.break_length,
                    "longer_break_length": task_entity.date_frame_definition.longer_break_length,
                    "gap_between_long_breaks": task_entity.date_frame_definition.gap_between_long_breaks,
                }
            )

        orm_task = self._get_for_update(task_entity.id)

        if orm_task is not None:
            orm_task.set(**values_to_update)
            self._persist_sub_tasks(orm_task, replace=True)

    def get(self, task_id: TaskId) -> Task:
        try:
            orm_task = TaskModel[task_id]
        except ObjectNotFound:
            raise NotFound(_("Task does not exist."))
        else:
            return self.to_domain_entity(orm_task)

    def save(self, task: Task, create: bool = False) -> None:
        if create:
            self._persist_new_orm_task(task)
        else:
            self._update_existing_orm_task(task)

    def delete(self, task_id: Task) -> None:
        orm_task = TaskModel.get(id=task_id)

        if orm_task is not None:
            orm_task.delete()
