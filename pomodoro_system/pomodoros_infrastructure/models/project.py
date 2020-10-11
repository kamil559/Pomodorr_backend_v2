import uuid
from datetime import datetime

from pony.orm import PrimaryKey, Required

from foundation.models import db


class Project(db.Entity):
    _table_ = 'projects'

    id = PrimaryKey(uuid.UUID, auto=False)
    name = Required(str, max_len=128)
    priority_color = Required(str, max_len=7)
    priority_level = Required(int)
    ordering = Required(int)
    owner_id = Required(uuid.UUID)
    created_at = Required(datetime)
    deleted_at = Required(datetime)
