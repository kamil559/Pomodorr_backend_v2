import uuid

from flask_security import PonyUserDatastore
from pony.orm import db_session


class PonyORMUserDatastore(PonyUserDatastore):
    @db_session
    def create_user(self, **kwargs):
        kwargs = self._prepare_create_user_args(**kwargs)
        identifier = uuid.uuid4()
        kwargs["id"] = identifier
        return super(PonyORMUserDatastore, self).create_user(**kwargs)
