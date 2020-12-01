from datetime import timedelta

from foundation.value_objects import DateFrameDefinition
from marshmallow import EXCLUDE, Schema, fields, post_load, validate


class DateFrameDefinitionSchema(Schema):
    pomodoro_length = fields.TimeDelta(
        required=True,
        allow_none=False,
        precision=fields.TimeDelta.MINUTES,
        validate=validate.Range(min=timedelta(minutes=1), max=timedelta(minutes=720)),
        minimum=1,
        maximum=720,
        type="integer",
        description="Interval (minutes)",
    )
    break_length = fields.TimeDelta(
        required=True,
        allow_none=False,
        precision=fields.TimeDelta.MINUTES,
        validate=validate.Range(min=timedelta(minutes=1), max=timedelta(minutes=720)),
        minimum=1,
        maximum=720,
        type="integer",
        description="Interval (minutes)",
    )
    longer_break_length = fields.TimeDelta(
        required=True,
        allow_none=False,
        precision=fields.TimeDelta.MINUTES,
        validate=validate.Range(min=timedelta(minutes=1), max=timedelta(minutes=720)),
        minimum=1,
        maximum=720,
        type="integer",
        description="Interval (minutes)",
    )
    gap_between_long_breaks = fields.Integer(
        required=True, allow_none=False, precision=fields.TimeDelta.MINUTES, validate=validate.Range(min=1), minimum=1
    )

    @post_load
    def to_dto(self, data: dict, **_kwargs) -> dict:
        return DateFrameDefinition(
            pomodoro_length=data.get("pomodoro_length", None),
            break_length=data.get("break_length", None),
            longer_break_length=data.get("longer_break_length", None),
            gap_between_long_breaks=data.get("gap_between_long_breaks", None),
        )

    class Meta:
        unknown = EXCLUDE
