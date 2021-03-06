import uuid
from datetime import datetime, timedelta

from foundation.models import db
from pomodoros.domain.value_objects import TaskStatus
from pony.orm import LongStr, Optional, PrimaryKey, Required, Set


class TaskModel(db.Entity):
    _table_ = "tasks"

    id = PrimaryKey(uuid.UUID, auto=False)
    project = Required("ProjectModel")
    name = Required(str, max_len=128)
    status = Required(int)
    priority_color = Required(str, max_len=7)
    priority_level = Required(int)
    ordering = Required(int)
    due_date = Optional(datetime)
    pomodoros_to_do = Required(int)
    pomodoros_burn_down = Required(int)
    pomodoro_length = Optional(timedelta)
    break_length = Optional(timedelta)
    longer_break_length = Optional(timedelta)
    gap_between_long_breaks = Optional(int)
    reminder_date = Optional(datetime)
    renewal_interval = Optional(timedelta)
    note = Optional(LongStr, lazy=False)
    created_at = Required(datetime)
    sub_tasks = Set("SubTaskModel", cascade_delete=True)
    pomodoros = Set("PomodoroModel", cascade_delete=True, lazy=True)

    @property
    def is_active(self) -> bool:
        return self.status == TaskStatus.ACTIVE.value


class SubTaskModel(db.Entity):
    _table_ = "sub_tasks"

    id = PrimaryKey(uuid.UUID, auto=False)
    name = Required(str, max_len=128)
    task = Required(TaskModel)
    ordering = Required(int)
    is_completed = Required(bool)
