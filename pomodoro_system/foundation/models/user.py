import uuid
from datetime import timedelta

from pony.orm import Database, PrimaryKey, Optional, Required

from foundation.value_objects import UserDateFrameDefinition as UserDateFrameDefinitionEntity

db = Database()


class User(db.Entity):
    _table_ = "users"

    id = PrimaryKey(uuid.UUID, auto=False)
    date_frame_definition = Optional(lambda: UserDateFrameDefinition, lazy=False)


class UserDateFrameDefinition(db.Entity):
    _table_ = "user_date_frame_definitions"

    id = PrimaryKey(uuid.UUID, auto=False)
    pomodoro_length = Required(timedelta, default=UserDateFrameDefinitionEntity.pomodoro_length)
    break_length = Required(timedelta, default=UserDateFrameDefinitionEntity.break_length)
    longer_break_length = Required(timedelta, default=UserDateFrameDefinitionEntity.longer_break_length)
    gap_between_long_breaks = Required(int, min=0, default=UserDateFrameDefinitionEntity.gap_between_long_breaks)
    user = Required(User)
