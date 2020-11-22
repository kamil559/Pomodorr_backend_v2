import functools
import http
from typing import Set

from flask import abort
from flask_jwt_extended import get_jwt_claims


def _current_user_roles() -> Set[str]:
    user_claims = get_jwt_claims()
    role_names = user_claims.get("roles") or None
    return set(role_names) if role_names is not None else set()


def _has_every_required_roles(required_roles: Set[str], user_roles: Set[str]) -> bool:
    return user_roles.issuperset(required_roles)


def _has_at_least_one_of_accepted_roles(accepted_roles: Set[str], user_roles: Set[str]) -> bool:
    return not user_roles.isdisjoint(accepted_roles)


def roles_required(*role_names):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            required_roles = set(str(role) for role in role_names)
            current_roles = _current_user_roles()

            if _has_every_required_roles(required_roles, current_roles):
                return func(*args, **kwargs)
            abort(http.HTTPStatus.FORBIDDEN)

        return wrapper

    return decorator


def roles_accepted(*role_names):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            accepted_roles = set(str(role) for role in role_names)
            current_roles = _current_user_roles()

            if _has_at_least_one_of_accepted_roles(accepted_roles, current_roles):
                return func(*args, **kwargs)
            abort(http.HTTPStatus.FORBIDDEN)

        return wrapper

    return decorator
