from foundation.value_objects import DateFrameDefinition
from marshmallow import Schema, fields


class UserDateFrameDefinition(DateFrameDefinition):
    getting_to_work_sound = ...
    break_time_sound = ...


class UserSchema(Schema):
    email = fields.Email(dump_only=True)

    date_frame_definition = fields.Nested(UserDateFrameDefinition)
