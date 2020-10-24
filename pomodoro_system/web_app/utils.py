from typing import Optional, Type

import marshmallow
from flask import abort, make_response, request
from marshmallow import Schema

from foundation.value_objects import T


def get_dto_or_abort(schema_class: Type[Schema], context: dict) -> Optional[T]:
    schema = schema_class(context=context)
    try:
        return schema.load({**request.get_json(), **context})
    except marshmallow.ValidationError as e:
        abort(make_response(e.messages, 400))
