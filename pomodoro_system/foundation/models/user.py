import uuid
from datetime import datetime, timedelta

from flask_security import RoleMixin, UserMixin
from foundation.value_objects import UserDateFrameDefinition as UserDateFrameDefinitionEntity
from pony.orm import Database, Optional, PrimaryKey, Required, Set

db = Database()


class Role(db.Entity, RoleMixin):
    id = PrimaryKey(uuid.UUID, auto=False)
    name = Required(str, unique=True)
    description = Optional(str)
    users = Set("User")


class User(db.Entity, UserMixin):
    _table_ = "users"

    id = PrimaryKey(uuid.UUID, auto=False)
    confirmed_at = Optional(datetime)
    email = Required(str, unique=True)
    password = Required(str)
    date_frame_definition = Optional("UserDateFrameDefinitionModel", lazy=False, cascade_delete=True)
    active = Required(bool, default=False)
    roles = Set(Role)

    def after_insert(self):
        user_date_frame_definition_data = {"id": uuid.uuid4(), "user": self.id}

        self.date_frame_definition = UserDateFrameDefinitionModel(**user_date_frame_definition_data)


class UserDateFrameDefinitionModel(db.Entity):
    _table_ = "user_date_frame_definitions"

    id = PrimaryKey(uuid.UUID, auto=False)
    pomodoro_length = Required(timedelta, default=UserDateFrameDefinitionEntity.pomodoro_length)
    break_length = Required(timedelta, default=UserDateFrameDefinitionEntity.break_length)
    longer_break_length = Required(timedelta, default=UserDateFrameDefinitionEntity.longer_break_length)
    gap_between_long_breaks = Required(int, min=0, default=UserDateFrameDefinitionEntity.gap_between_long_breaks)
    user = Required("User")
