from typing import Optional, Type

import marshmallow
from flask import Blueprint, abort, make_response, request
from flask_apispec.views import MethodResourceMeta
from foundation.value_objects import T
from marshmallow import Schema


def get_dto_or_abort(schema_class: Type[Schema], context: dict) -> Optional[T]:
    schema = schema_class(context=context)
    try:
        request_json = request.get_json() or {}
        return schema.load({**request_json, **context})
    except marshmallow.ValidationError as e:
        abort(make_response(e.messages, 400))


def load_int_query_parameter(query_parameter: str) -> Optional[int]:
    if query_parameter:
        try:
            return int(query_parameter)
        except ValueError:
            return None


class RegistrableBlueprint(Blueprint):
    def __init__(self, *args, **kwargs) -> None:
        self.view_functions = []
        super(RegistrableBlueprint, self).__init__(*args, **kwargs)

    @staticmethod
    def _has_injector_bindings(view_cls) -> bool:
        return hasattr(view_cls.__init__, "__bindings__")

    @staticmethod
    def _get_injector_bindings(view_cls) -> dict:
        return getattr(view_cls.__init__, "__bindings__")

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        injector_bindings = {}
        if hasattr(view_func, "view_class") and isinstance(view_func.view_class, MethodResourceMeta):
            if self._has_injector_bindings(view_func.view_class):
                injector_bindings = self._get_injector_bindings(view_func.view_class)

            self.view_functions.append((view_func.view_class, endpoint, injector_bindings))
        else:
            self.view_functions.append((view_func, endpoint, injector_bindings))
        super(RegistrableBlueprint, self).add_url_rule(rule, endpoint, view_func, **options)
