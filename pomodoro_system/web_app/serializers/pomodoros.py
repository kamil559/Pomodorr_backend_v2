import pytz
from marshmallow import fields, Schema, post_load, EXCLUDE

from pomodoros import BeginPomodoroInputDto, PausePomodoroInputDto


class BeginPomodoroSchema(Schema):
    task_id = fields.UUID(required=True)
    start_date = fields.AwareDateTime(required=True, allow_none=False, default_timezone=pytz.UTC)
    id = fields.UUID(required=True, dump_only=True)
    frame_type = fields.Function(dump_only=True, serialize=lambda obj: obj.frame_type.value)

    class Meta:
        unknown = EXCLUDE

    @post_load
    def map_to_dto(self, data: dict, **kwargs) -> BeginPomodoroInputDto:
        return BeginPomodoroInputDto(**data)


class PausePomodoroSchema(Schema):
    pomodoro_id = fields.UUID(required=True)
    pause_date = fields.AwareDateTime(required=True, allow_none=False, default_timezone=pytz.UTC)

    class Meta:
        unknown = EXCLUDE

    @post_load()
    def map_to_dto(self, data: dict, **_kwargs) -> PausePomodoroInputDto:
        return PausePomodoroInputDto(**data)
