import uuid
from datetime import datetime

from foundation.models import db
from pony.orm import Optional, PrimaryKey, Required


class Token(db.Entity):
    _table_ = "tokens"

    id = PrimaryKey(uuid.UUID, auto=True)
    jti = Required(str, 36)
    token_type = Required(str, 10)
    user_identity = Required(uuid.UUID)
    revoked = Required(bool)
    expires = Required(datetime)
    browser = Optional(str)
    platform = Optional(str)
    ip_address = Required(str)
