import uuid
from datetime import datetime

from pony.orm import PrimaryKey, Required, Optional, Set

from foundation.models import db


class DateFrame(db.Entity):
    _table_ = 'date_frames'

    id = PrimaryKey(uuid.UUID, auto=False)
    frame_type = Required(int)
    start_date = Required(datetime, sql_type='TIMESTAMP WITH TIME ZONE')
    end_date = Optional(datetime, sql_type='TIMESTAMP WITH TIME ZONE')


class Pomodoro(DateFrame):
    task_id = Required(uuid.UUID)
    contained_pauses = Set(lambda: Pause)


class Pause(DateFrame):
    pomodoro = Required(Pomodoro)
