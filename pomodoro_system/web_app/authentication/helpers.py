from datetime import datetime
from typing import List, Optional, Tuple, Type
from uuid import UUID

import pytz
from flask import current_app, request, url_for
from flask_jwt_extended import decode_token, get_jwt_identity
from flask_security.confirmable import generate_confirmation_token
from flask_security.utils import get_token_status, verify_hash
from foundation.exceptions import DomainValidationError, NotFound
from foundation.i18n import N_
from foundation.models import User
from foundation.value_objects import UserId
from pony.orm import ObjectNotFound, desc, select
from web_app.authentication.models.token import Token
from werkzeug.local import LocalProxy

_security = LocalProxy(lambda: current_app.extensions["security"])


def _epoch_utc_to_datetime(epoch_utc):
    return datetime.fromtimestamp(epoch_utc)


def _get_user_agent_data() -> dict:
    if "X-Forwarded-For" in request.headers:
        remote_address = request.headers.getlist("X-Forwarded-For")[0].rpartition(" ")[-1]
    else:
        remote_address = request.remote_addr or "Untrackable"

    return {
        "browser": getattr(request.user_agent, "browser") or "Untrackable",
        "platform": getattr(request.user_agent, "platform") or "Untrackable",
        "ip_address": remote_address,
    }


def add_token_to_database(encoded_token, identity_claim: str = None):
    identity_claim = current_app.config["JWT_IDENTITY_CLAIM"] if identity_claim is None else identity_claim
    decoded_token = decode_token(encoded_token)
    jti = decoded_token["jti"]
    token_type = decoded_token["type"]
    user_identity = decoded_token[identity_claim]
    expires = _epoch_utc_to_datetime(decoded_token["exp"])
    revoked = False
    user_agent_data = _get_user_agent_data()

    Token(
        jti=jti, token_type=token_type, user_identity=user_identity, expires=expires, revoked=revoked, **user_agent_data
    )


def is_token_revoked(decoded_token):
    jti = decoded_token["jti"]
    return Token.exists(jti=jti, revoked=True)


def get_token(**filter_kwargs) -> Optional[Type[Token]]:
    try:
        return Token.select().filter(**filter_kwargs).get()
    except ObjectNotFound:
        raise NotFound(N_("The token was not found."))


def get_user_tokens(user_identity, **additional_filters) -> List[Token]:
    return Token.select().filter(user_identity=user_identity, **additional_filters).sort_by(desc(Token.expires))


def revoke_all_tokens(user_identity):
    user_active_tokens = get_user_tokens(user_identity, revoked=False)

    # PonyORM does not support bulk update
    for token in user_active_tokens:
        token.revoked = True


def update_token(token: Type[Token], token_data: dict) -> Optional[Type[Token]]:
    token.set(**token_data)
    return token


def prune_expired_tokens():
    now = datetime.now(tz=pytz.UTC)
    Token.select(lambda token: token.expires <= now).delete()


def executes_self_action(user_id: UserId) -> bool:
    current_user_id = get_jwt_identity()
    return user_id == UUID(current_user_id)


def generate_email_change_link(user: User) -> str:
    confirmation_token = generate_confirmation_token(user)
    return url_for("auth.confirm_email_change", confirmation_token=confirmation_token, _external=True)


def check_can_change_email_address(new_email: str) -> bool:
    existing_user_id = select(user.id for user in User if user.email == new_email).get()

    if existing_user_id is not None:
        if executes_self_action(existing_user_id):
            raise DomainValidationError({"email": N_("New email must be different than the current one.")})
        else:
            raise DomainValidationError(
                {"email": N_("%(email)s is already associated with an account.") % {"email": new_email}}
            )


def change_email_token_status(token: str) -> Optional[Tuple]:
    expired, invalid, user, token_data = get_token_status(token, "confirm", "CONFIRM_EMAIL", return_data=True)

    if not invalid and user:
        user_id, token_email_hash = token_data
        invalid = not verify_hash(token_email_hash, user.email)
    return expired, invalid, user
