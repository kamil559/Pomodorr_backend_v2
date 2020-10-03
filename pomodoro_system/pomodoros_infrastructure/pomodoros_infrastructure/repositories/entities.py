import uuid
from datetime import datetime, timedelta

from injector import inject
from pony.orm import Database, PrimaryKey, Required, Optional, Set


@inject
class DatabaseProxy:
    database: Database


class Project(DatabaseProxy.database.Entity):
    _table_ = 'projects'

    id = PrimaryKey(uuid.UUID, auto=False)
    name = Required(str)
    priority_color = Required(str)
    priority_level = Required(int)
    ordering = Required(int)
    owner_id = Required(uuid.UUID)
    created_at = Required(datetime)
    deleted_at = Required(datetime)


class Task(DatabaseProxy.database.Entity):
    _table_ = 'tasks'

    id = PrimaryKey(uuid.UUID, auto=False)
    project_id = Required(uuid.UUID)
    name = Required(str)
    status = Required(int)
    priority_color = Required(str)
    priority_level = Required(int)
    ordering = Required(int)
    due_date = Optional(datetime)
    pomororos_to_do = Required(int)
    pomodoros_burn_down = Required(int)
    pomodoro_length = Optional(timedelta)
    break_length = Optional(timedelta)
    longer_break_length = Optional(timedelta)
    gap_between_long_breaks = Optional(int)
    reminder_date = Optional(datetime)
    renewal_interval = Optional(timedelta)
    note = Optional(str)
    created_at = Required(datetime)
    sub_tasks = Set(lambda: SubTask)


class SubTask(DatabaseProxy.database.Entity):
    _table_ = 'sub_tasks'

    id = PrimaryKey(uuid.UUID, auto=False)
    name = Required(str)
    task = Required(Task)
    created_at = Required(datetime)
    is_completed = Required(bool)


class DateFrame(DatabaseProxy.database.Entity):
    id = PrimaryKey(uuid.UUID, auto=False)
    frame_type = Required(int)
    start_date = Required(datetime)
    end_date = Optional(datetime)


class Pomodoro(DateFrame):
    _table_ = "pomodoros"

    task_id = Required(uuid.UUID)
    contained_pauses = Set(lambda: Pause)


class Pause(DateFrame):
    _table_ = 'pauses'

    pomodoro = Required(Pomodoro)
