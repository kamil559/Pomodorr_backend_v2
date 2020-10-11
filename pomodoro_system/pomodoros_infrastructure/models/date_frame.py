import uuid
from datetime import datetime

from pony.orm import PrimaryKey, Required, Optional, Set

from foundation.models import db


class DateFrame(db.Entity):
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
