from datetime import datetime
from gettext import gettext as _
from typing import Optional, Type

import pytz
from flask import current_app, request
from flask_jwt_extended import decode_token
from foundation.exceptions import NotFound
from pony.orm import ObjectNotFound, desc
from web_app.authentication.models.token import Token


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
        raise NotFound(_("The token was not found."))


def get_user_tokens(user_identity):
    return Token.select().filter(user_identity=user_identity).sort_by(desc(Token.expires))


def update_token(token: Type[Token], token_data: dict) -> Optional[Type[Token]]:
    token.set(**token_data)
    return token


def prune_database():
    now = datetime.now(tz=pytz.UTC)
    Token.select(lambda token: token.revoked and token.expires <= now).delete()
