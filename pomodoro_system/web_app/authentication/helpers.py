from datetime import datetime
from gettext import gettext as _

import pytz
from flask_jwt_extended import decode_token
from foundation.exceptions import NotFound
from pony.orm import ObjectNotFound
from web_app.authentication.models.token import Token


def _epoch_utc_to_datetime(epoch_utc):
    return datetime.fromtimestamp(epoch_utc)


def add_token_to_database(encoded_token, identity_claim):
    decoded_token = decode_token(encoded_token)
    jti = decoded_token["jti"]
    token_type = decoded_token["type"]
    user_identity = decoded_token[identity_claim]
    expires = _epoch_utc_to_datetime(decoded_token["exp"])
    revoked = False

    Token(
        jti=jti,
        token_type=token_type,
        user_identity=user_identity,
        expires=expires,
        revoked=revoked,
    )


def is_token_revoked(decoded_token):
    jti = decoded_token["jti"]
    return Token.exists(jti=jti, revoked=True)


def get_user_tokens(user_identity):
    return Token.select().filter(user_identity=user_identity)


def revoke_token(token_id, user):
    try:
        token = Token.query.filter_by(id=token_id, user_identity=user).one()
        token.revoked = True
    except ObjectNotFound:
        raise NotFound(_("The token was not found."))


def legalize_token(token_id, user):
    try:
        token = Token.query.filter_by(id=token_id, user_identity=user).one()
        token.revoked = False
    except ObjectNotFound:
        raise NotFound(_("The token was not found."))


def prune_database():
    now = datetime.now(tz=pytz.UTC)
    Token.select(lambda token: token.revoked and token.expires < now).delete()
