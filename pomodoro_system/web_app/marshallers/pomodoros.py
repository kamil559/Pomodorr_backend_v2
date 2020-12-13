import pytz
from marshmallow import EXCLUDE, Schema, fields, post_load, pre_dump
from pomodoros import BeginPomodoroInputDto, FinishPomodoroInputDto, PausePomodoroInputDto, ResumePomodoroInputDto


class BeginPomodoroSchema(Schema):
    task_id = fields.UUID(required=True)
    start_date = fields.AwareDateTime(required=True, allow_none=False, default_timezone=pytz.UTC)
    id = fields.UUID(required=True, dump_only=True)
    frame_type = fields.Integer(dump_only=True)

    class Meta:
        unknown = EXCLUDE

    @pre_dump
    def serialize_fields(self, pre_serialized_object: dict, many=False):
        pre_serialized_object.frame_type = pre_serialized_object.frame_type.value
        return pre_serialized_object

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


class ResumePomodoroSchema(Schema):
    pomodoro_id = fields.UUID(required=True)
    resume_date = fields.AwareDateTime(required=True, allow_none=False, default_timezone=pytz.UTC)

    class Meta:
        unknown = EXCLUDE

    @post_load()
    def make_dto(self, data: dict, **_kwargs):
        return ResumePomodoroInputDto(**data)


class FinishPomodoroSchema(Schema):
    id = fields.UUID(required=True)
    end_date = fields.AwareDateTime(required=True, allow_none=False, default_timezone=pytz.UTC)
    owner_id = fields.UUID(required=True, load_only=True)
    start_date = fields.AwareDateTime(dump_only=True, default_timezone=pytz.UTC)
    frame_type = fields.Integer(dump_only=True)

    class Meta:
        unknown = EXCLUDE

    @pre_dump
    def serialize_fields(self, pre_serialized_object: dict, many=False):
        pre_serialized_object.frame_type = pre_serialized_object.frame_type.value
        return pre_serialized_object

    @post_load()
    def make_dto(self, data: dict, **_kwargs) -> FinishPomodoroInputDto:
        return FinishPomodoroInputDto(**data)
