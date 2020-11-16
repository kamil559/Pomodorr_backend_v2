from foundation.value_objects import Priority, PriorityLevel
from marshmallow import EXCLUDE, Schema, fields, post_load, pre_dump, validate
from web_app.serializers.fields.color import ColorField


class PrioritySchema(Schema):
    color = ColorField(required=True, allow_none=False)
    priority_level = fields.Integer(
        required=False,
        allow_none=True,
        default=PriorityLevel.NO_PRIORITY.value,
        validate=validate.Range(min=0, max=3),
        minimum=0,
        maximum=3,
    )

    @pre_dump
    def transform_fields(self, pre_serialized_object: Priority, **_kwargs) -> dict:
        pre_serialized_object.priority_level = pre_serialized_object.priority_level.value
        return pre_serialized_object

    @post_load
    def to_dto(self, data: dict, **_kwargs) -> dict:
        return Priority(
            color=data.get("color") or Priority.color,
            priority_level=PriorityLevel(data.get("priority_level") or Priority.priority_level.value),
        )

    class Meta:
        unknown = EXCLUDE
