import pytz
from marshmallow import Schema, fields, post_load, EXCLUDE

from pomodoros import CompleteTaskInputDto


class CompleteTaskSchema(Schema):
    id = fields.UUID(required=True)
    completed_at = fields.AwareDateTime(required=True, allow_none=False, default_timezone=pytz.UTC)

    class Meta:
        unknown = EXCLUDE

    @post_load()
    def make_dto(self, data: dict, **_kwargs):
        return CompleteTaskInputDto(**data)
