import http

from flask import abort
from foundation.interfaces import ResourceProtector
from foundation.value_objects import UserId


class UserProtector(ResourceProtector):
    def authorize(self, requester_id: UserId, resource_id: UserId, abort_if_none: bool = True) -> None:
        if requester_id != resource_id:
            abort(http.HTTPStatus.FORBIDDEN)
