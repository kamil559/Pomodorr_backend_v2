import uuid
from datetime import datetime

import marshmallow_dataclass
from foundation.utils import to_utc
from foundation.value_objects import Priority
from marshmallow import EXCLUDE, fields, post_load
from pomodoros.domain.entities import Project
from web_app.marshallers.priority import PrioritySchema

BaseProjectRestSchema = marshmallow_dataclass.class_schema(Project)


class ProjectRestSchema(BaseProjectRestSchema):
    priority = fields.Nested(PrioritySchema, required=False, allow_none=True)

    def populate_partial_data(self, request_data: dict) -> dict:
        pre_populated_data = {
            "priority": request_data.get("priority") or Priority(),
        }

        project_instance: Project = self.context["project_instance"]
        pre_populated_data["owner_id"] = project_instance.owner_id
        for schema_field in self.fields.keys():
            pre_populated_data.setdefault(schema_field, getattr(project_instance, str(schema_field)))

        return pre_populated_data

    @post_load
    def populate_default_values(self, data: dict, partial: bool = False, **_kwargs) -> dict:
        if partial:
            default_values = self.populate_partial_data(data)
        else:
            default_values = {
                "id": uuid.uuid4(),
                "created_at": to_utc(datetime.now()),
                "owner_id": self.context["owner_id"],
                "priority": data.get("priority") or Priority(),
            }
        data.update(default_values)
        return data

    class Meta:
        unknown = EXCLUDE
        exclude = ("owner_id", "deleted_at")
        dump_only = ("id", "created_at", "owner_id")
