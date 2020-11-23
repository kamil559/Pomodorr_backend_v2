import uuid
from gettext import gettext as _

from flask_security import PonyUserDatastore
from flask_security.utils import get_identity_attributes
from foundation.exceptions import NotFound
from pony.orm import db_session


class PonyORMUserDatastore(PonyUserDatastore):
    @db_session
    def create_user(self, **kwargs):
        kwargs = self._prepare_create_user_args(**kwargs)
        identifier = uuid.uuid4()
        kwargs["id"] = identifier
        return super(PonyORMUserDatastore, self).create_user(**kwargs)

    @db_session
    def add_role_to_user(self, user, role):
        user, role = self._prepare_role_modify_args(user, role)
        if role not in user.roles:
            user.roles.add(role)
            return True
        return False

    @db_session
    def get_user(self, identifier, consider_banned: bool = False, raise_if_not_found: bool = False):
        from pony.orm.core import ObjectNotFound

        user = None

        try:
            user = self.user_model[identifier]
        except (ObjectNotFound, ValueError):
            for attr in get_identity_attributes():
                # this is a nightmare, tl;dr we need to get the thing that
                # corresponds to email (usually)
                try:
                    user = self.user_model.get(**{attr: identifier})
                except (TypeError, ValueError):
                    pass
        finally:
            if user is not None and (not user.is_banned or (user.is_banned and consider_banned)):
                return user
            else:
                if raise_if_not_found:
                    raise NotFound({_("User does not exist.")})
