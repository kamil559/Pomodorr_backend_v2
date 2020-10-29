from typing import Optional, Type

import marshmallow
from flask import Blueprint, abort, make_response, request
from foundation.value_objects import T
from marshmallow import Schema


def get_dto_or_abort(schema_class: Type[Schema], context: dict) -> Optional[T]:
    schema = schema_class(context=context)
    try:
        request_json = request.get_json() or {}
        return schema.load({**request_json, **context})
    except marshmallow.ValidationError as e:
        abort(make_response(e.messages, 400))


class RegistrableBlueprint(Blueprint):
    def __init__(self, *args, **kwargs) -> None:
        self.view_functions = []
        super(RegistrableBlueprint, self).__init__(*args, **kwargs)

    def route(self, rule, **options):
        def decorator(f):
            endpoint = options.pop("endpoint", f.__name__)
            self.view_functions.append(f)
            self.add_url_rule(rule, endpoint, f, **options)
            return f

        return decorator
