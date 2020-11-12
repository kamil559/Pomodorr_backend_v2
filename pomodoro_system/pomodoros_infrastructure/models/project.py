import uuid
from datetime import datetime

from foundation.models import db
from pony.orm import Optional, PrimaryKey, Required, Set


class ProjectModel(db.Entity):
    _table_ = "projects"

    id = PrimaryKey(uuid.UUID, auto=False)
    name = Required(str, max_len=128)
    priority_color = Required(str, max_len=7)
    priority_level = Required(int)
    ordering = Required(int)
    owner_id = Required(uuid.UUID)
    created_at = Required(datetime)
    deleted_at = Optional(datetime)
    tasks = Set("TaskModel", cascade_delete=True, lazy=True)

    @property
    def is_removed(self):
        return self.deleted_at is not None
