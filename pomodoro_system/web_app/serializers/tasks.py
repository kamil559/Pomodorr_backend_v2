import pytz
from marshmallow import Schema, fields, post_load, EXCLUDE

from pomodoros import (
    CompleteTaskInputDto,
    ReactivateTaskInputDto,
    PinTaskToProjectInputDto,
)


class CompleteTaskSchema(Schema):
    id = fields.UUID(required=True)
    completed_at = fields.AwareDateTime(required=True, allow_none=False, default_timezone=pytz.UTC)

    class Meta:
        unknown = EXCLUDE

    @post_load()
    def make_dto(self, data: dict, **_kwargs):
        return CompleteTaskInputDto(**data)


class ReactivateTaskSchema(Schema):
    id = fields.UUID(required=True)
    status = fields.Function(dump_only=True, serialize=lambda task: task.status.value)

    class Meta:
        unknown = EXCLUDE

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
