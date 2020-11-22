import http
import uuid
from gettext import gettext as _

from flask import abort
from foundation.exceptions import DomainValidationError
from foundation.interfaces import ResourceProtector
from foundation.value_objects import UserId
from pony.orm import select
from web_app.authentication.models.token import Token


class TokenProtector(ResourceProtector):
    def authorize(self, requester_id: UserId, resource_id: uuid.UUID, abort_request: bool = True) -> None:
        token_id, token_owner_id = select(
            (token.id, token.user_identity) for token in Token if token.id == resource_id
        ).get() or (None, None)

        if token_id is None:
            if abort_request:
                abort(http.HTTPStatus.NOT_FOUND)
            else:
                raise DomainValidationError({"token_id": _("Selected token does not exist.")})

        if requester_id != token_owner_id:
            abort(http.HTTPStatus.FORBIDDEN)
