import pytz
from marshmallow import fields, Schema, post_load, EXCLUDE

from pomodoros import BeginPomodoroInputDto


class BeginPomodoroSchema(Schema):
    task_id = fields.UUID(required=True)
    start_date = fields.AwareDateTime(required=True, allow_none=False, default_timezone=pytz.UTC)
    id = fields.UUID(required=True, dump_only=True)
    frame_type = fields.Function(dump_only=True, serialize=lambda obj: obj.frame_type.value)

    class Meta:
        unknown = EXCLUDE

    @post_load
    def make_dto(self, data: dict, **kwargs) -> BeginPomodoroInputDto:
        return BeginPomodoroInputDto(**data)
