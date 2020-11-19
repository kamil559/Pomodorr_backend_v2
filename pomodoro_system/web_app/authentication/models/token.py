import uuid
from datetime import datetime

from foundation.models import db
from pony.orm import Required


class Token(db.Entity):
    id = Required(uuid.UUID)
    jti = Required(str, 36)
    token_type = Required(str, 10)
    user_identity = Required(uuid.UUID)
    revoked = Required(bool)
    expires = Required(datetime)

    def to_dict(self) -> dict:
        return {
            "token_id": self.id,
            "jti": self.jti,
            "token_type": self.token_type,
            "user_identity": self.user_identity,
            "revoked": self.revoked,
            "expires": self.expires,
        }
