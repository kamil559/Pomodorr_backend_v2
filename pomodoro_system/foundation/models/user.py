import typing
import uuid
from datetime import datetime, timedelta

from flask_security import UserMixin
from foundation.value_objects import UserDateFrameDefinition as UserDateFrameDefinitionEntity
from pony.orm import Database, Optional, PrimaryKey, Required, Set, exists

db = Database()


class Role(db.Entity):
    name = Required(str, unique=True)
    description = Optional(str)
    users = Set("User")

    @staticmethod
    def get_permissions():
        return set()


class User(db.Entity, UserMixin):
    _table_ = "users"

    id = PrimaryKey(uuid.UUID, auto=False)
    confirmed_at = Optional(datetime)
    email = Required(str, unique=True)
    unconfirmed_new_email = Optional(str)
    password = Required(str)
    date_frame_definition = Optional("UserDateFrameDefinitionModel", lazy=False, cascade_delete=True)
    active = Required(bool, default=False)
    roles = Set("Role")
    ban_records = Set("UserBanRecord", cascade_delete=True)
    projects = Set("ProjectModel", lazy=True, cascade_delete=True)
    avatar = Optional(str)

    @property
    def is_banned(self) -> bool:
        return exists(
            ban_record
            for ban_record in self.ban_records
            if (not ban_record.manually_unbanned and ban_record.banned_until >= datetime.utcnow())
            or (ban_record.is_permanent and not ban_record.manually_unbanned)
        )

    @property
    def current_ban_record(self) -> typing.Optional[typing.Type["UserBanRecord"]]:
        ban_record_query = (
            self.ban_records.filter(
                lambda record: (not record.manually_unbanned and record.banned_until >= datetime.utcnow())
                or (record.is_permanent and not record.manually_unbanned)
            )
            or None
        )

        if ban_record_query is not None:
            return max(ban_record_query.for_update())

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
    getting_to_work_sound = Required(str, default=UserDateFrameDefinitionEntity.getting_to_work_sound)
    break_time_sound = Required(str, default=UserDateFrameDefinitionEntity.break_time_sound)
    user = Required("User")


class UserBanRecord(db.Entity):
    _table_ = "user_ban_records"

    id = PrimaryKey(uuid.UUID, auto=True)
    user = Required("User")
    banned_until = Optional(datetime)
    is_permanent = Required(bool, default=False)
    ban_reason = Optional(str)
    manually_unbanned = Required(bool, default=False)
    manually_unbanned_at = Optional(datetime)
