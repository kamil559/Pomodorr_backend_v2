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
from pomodoros_infrastructure.queries.tasks import DueDateFilter
from web_app.marshallers.priority import PrioritySchema


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
    ordering = fields.Integer(required=True, allow_none=False, validate=validate.Range(min=1), minimum=1)
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
    sub_tasks = fields.Nested(SubTaskRestSchema(many=True), required=False, allow_none=True)
    project_id = fields.UUID(required=True, allow_none=False)

    @pre_dump
    def transform_fields(self, pre_serialized_object: Task, **_kwargs) -> dict:
        pre_serialized_object.status = pre_serialized_object.status.value
        return pre_serialized_object

    def populate_partial_data(self, request_data: dict) -> dict:
        task_instance = self.context["task_instance"]
        pre_populated_data = {
            "project_id": task_instance.project_id,
            "priority": request_data.get("priority") or Priority(),
            "date_frame_definition": request_data.get("date_frame_definition") or None,
            "sub_tasks": request_data.get("sub_tasks") or [],
        }
        request_data.update(pre_populated_data)

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
                "sub_tasks": data.get("sub_tasks") or [],
            }
        data.update(default_values)
        return data

    class Meta:
        unknown = EXCLUDE
        dump_only = ("id", "created_at", "status", "pomodoros_burn_down")


class TaskFilterSchema(Schema):
    project = fields.UUID(required=False, allow_none=True)
    due_date_rule = fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.OneOf(
            {
                DueDateFilter.RECENT.value,
                DueDateFilter.TODAY.value,
                DueDateFilter.TOMORROW.value,
                DueDateFilter.UPCOMING.value,
            }
        ),
        enum=[
            DueDateFilter.RECENT.value,
            DueDateFilter.TODAY.value,
            DueDateFilter.TOMORROW.value,
            DueDateFilter.UPCOMING.value,
        ],
        description="0 = Recent tasks,\n 1 = Today tasks,\n 2 = Tomorrow tasks,\n 3 = Upcoming tasks",
    )

    priority_level = fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.OneOf(
            [
                PriorityLevel.NO_PRIORITY.value,
                PriorityLevel.LOW_PRIORITY.value,
                PriorityLevel.MID_PRIORITY.value,
                PriorityLevel.HIGH_PRIORITY.value,
            ]
        ),
        enum=[
            PriorityLevel.NO_PRIORITY.value,
            PriorityLevel.LOW_PRIORITY.value,
            PriorityLevel.MID_PRIORITY.value,
            PriorityLevel.HIGH_PRIORITY.value,
        ],
        description="0 = No priority,\n 1 = Low priority,\n 2 = Mid priority,\n 3 = High priority",
    )
    status = fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.OneOf({TaskStatus.ACTIVE.value, TaskStatus.COMPLETED.value}),
        enum=[TaskStatus.ACTIVE.value, TaskStatus.COMPLETED.value],
        description="0 = Active,\n 1 = Completed",
    )

    @post_load
    def transform_due_date(self, data: dict, **_kwargs) -> dict:
        due_date = data.pop("due_date_rule", None)

        if due_date is not None:
            data["due_date_rule"] = DueDateFilter(due_date)
        return data

    class Meta:
        unknown = EXCLUDE


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
