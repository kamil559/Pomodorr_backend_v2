import uuid
from datetime import datetime

from foundation.models import db
from pomodoros.domain.value_objects import FrameType
from pony.orm import Optional, PrimaryKey, Required, Set


class PomodoroModel(db.Entity):
    _table_ = "pomodoros"

    id = PrimaryKey(uuid.UUID, auto=False)
    frame_type = Required(int, default=FrameType.TYPE_POMODORO.value)
    start_date = Required(datetime)
    end_date = Optional(datetime)
    task = Required("TaskModel")
    contained_pauses = Set(lambda: PauseModel)


class PauseModel(db.Entity):
    _table_ = "pauses"

    id = PrimaryKey(uuid.UUID, auto=False)
    frame_type = Required(int, default=FrameType.TYPE_PAUSE.value)
    start_date = Required(datetime)
    end_date = Optional(datetime)
    pomodoro = Required(PomodoroModel)
