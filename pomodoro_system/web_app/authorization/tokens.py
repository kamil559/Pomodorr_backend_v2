import http
import uuid

from flask import abort
from foundation.exceptions import DomainValidationError
from foundation.i18n import N_
from foundation.interfaces import ResourceProtector
from foundation.value_objects import UserId
from pony.orm import select
from web_app.authentication.models.token import Token


class TokenProtector(ResourceProtector):
    def authorize(self, requester_id: UserId, resource_id: uuid.UUID, abort_if_none: bool = True) -> None:
        token_id, token_owner_id = select(
            (token.id, token.user_identity) for token in Token if token.id == resource_id
        ).get() or (None, None)

        if token_id is None:
            if abort_if_none:
                abort(http.HTTPStatus.NOT_FOUND)
            else:
                raise DomainValidationError({"token_id": N_("Selected token does not exist.")})

        if requester_id != token_owner_id:
            abort(http.HTTPStatus.FORBIDDEN)
