import uuid
from datetime import datetime, timedelta

import marshmallow_dataclass
import pytz
from foundation.utils import to_utc
from foundation.value_objects import DateFrameDefinition, Priority, PriorityLevel
from marshmallow import EXCLUDE, Schema, fields, post_load, pre_dump, validate
from pomodoros import CompleteTaskInputDto, PinTaskToProjectInputDto, ReactivateTaskInputDto
from pomodoros.domain.entities import SubTask, Task
from pomodoros.domain.value_objects import TaskStatus


class PrioritySchema(Schema):
    color = fields.String(required=False, allow_none=True, default=Priority.color)
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


class SubTaskRestSchema(Schema):
    name = fields.String(required=True, allow_none=False)
    is_completed = fields.Boolean(required=True, allow_none=False, default=False)
    ordering = fields.Integer(required=True, allow_none=False, validate=validate.Range(min=1), minimum=1)

    @post_load
    def to_dto(self, data: dict, **_kwargs) -> SubTask:
        return SubTask(
            id=uuid.uuid4(),
            name=data.get("name"),
            ordering=data.get("ordering"),
            is_completed=data.get("is_completed", False),
        )

    class Meta:
        unknown = EXCLUDE


BaseTaskRestSchema = marshmallow_dataclass.class_schema(Task)


class TaskRestSchema(BaseTaskRestSchema):
    priority = fields.Nested(PrioritySchema, required=False, allow_none=True)
    date_frame_definition = fields.Nested(DateFrameDefinitionSchema, required=False, allow_none=True)
    renewal_interval = fields.TimeDelta(
        required=False,
        allow_none=True,
        precision=fields.TimeDelta.DAYS,
        validate=validate.Range(min=timedelta(days=1)),
        minimum=1,
        type="integer",
        description="Interval (days)",
    )
    status = fields.Integer()
    sub_tasks = fields.Nested(SubTaskRestSchema(many=True))
    project_id = fields.UUID(required=True, allow_none=False)

    @pre_dump
    def transform_fields(self, pre_serialized_object: Task, **_kwargs) -> dict:
        pre_serialized_object.status = pre_serialized_object.status.value
        return pre_serialized_object

    def populate_partial_data(self, request_data: dict) -> dict:
        task_instance = self.context["task_instance"]
        request_data["project_id"] = task_instance.project_id
        for schema_field in self.fields.keys():
            request_data.setdefault(schema_field, getattr(task_instance, str(schema_field)))

        return request_data

    @post_load
    def populate_default_values(self, data: dict, partial: bool = False, **_kwargs) -> dict:
        if partial:
            default_values = self.populate_partial_data(data)
        else:
            default_values = {
                "id": uuid.uuid4(),
                "created_at": to_utc(datetime.now()),
                "status": TaskStatus(TaskStatus.ACTIVE),
                "pomodoros_burn_down": 0,
                "date_frame_definition": data.get("date_frame_definition", None),
                "priority": data.get("priority") or Priority(),
            }
        data.update(default_values)
        return data

    class Meta:
        unknown = EXCLUDE
        dump_only = ("id", "created_at", "status", "pomodoros_burn_down")


class CompleteTaskSchema(Schema):
    id = fields.UUID(required=True)
    completed_at = fields.AwareDateTime(required=True, allow_none=False, default_timezone=pytz.UTC)
    new_task_id = fields.UUID(dump_only=True, required=False, allow_none=True)

    class Meta:
        unknown = EXCLUDE

    @post_load
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

    @post_load
    def make_dto(self, data: dict, **_kwargs) -> ReactivateTaskInputDto:
        return ReactivateTaskInputDto(**data)


class PinTaskToProjectSchema(Schema):
    id = fields.UUID(required=True)
    new_project_id = fields.UUID(required=True)

    class Meta:
        unknown = EXCLUDE

    @post_load
    def make_dto(self, data: dict, **_kwargs) -> PinTaskToProjectInputDto:
        return PinTaskToProjectInputDto(**data)
