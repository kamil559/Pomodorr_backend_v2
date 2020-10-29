import pytz
from marshmallow import EXCLUDE, Schema, fields, post_load, pre_dump
from pomodoros import CompleteTaskInputDto, PinTaskToProjectInputDto, ReactivateTaskInputDto


class CompleteTaskSchema(Schema):
    id = fields.UUID(required=True)
    completed_at = fields.AwareDateTime(required=True, allow_none=False, default_timezone=pytz.UTC)
    new_task_id = fields.UUID(dump_only=True, required=False, allow_none=True)

    class Meta:
        unknown = EXCLUDE

    @post_load()
    def make_dto(self, data: dict, **_kwargs):
        return CompleteTaskInputDto(**data)


class ReactivateTaskSchema(Schema):
    id = fields.UUID(required=True)
    status = fields.Integer(dump_only=True)

    class Meta:
        unknown = EXCLUDE

    @pre_dump
    def serialize_fields(self, pre_serialized_object: dict, many=False):
        pre_serialized_object.status = pre_serialized_object.status.value
        return pre_serialized_object

    @post_load()
    def make_dto(self, data: dict, **_kwargs) -> ReactivateTaskInputDto:
        return ReactivateTaskInputDto(**data)


class PinTaskToProjectSchema(Schema):
    id = fields.UUID(required=True)
    new_project_id = fields.UUID(required=True)

    class Meta:
        unknown = EXCLUDE

    @post_load()
    def make_dto(self, data: dict, **_kwargs) -> PinTaskToProjectInputDto:
        return PinTaskToProjectInputDto(**data)
