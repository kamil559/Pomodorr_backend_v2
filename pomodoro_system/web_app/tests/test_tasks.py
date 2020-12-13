from pony.orm import db_session
from web_app.authentication.models.token import Token
from web_app.celery_tasks import remove_expired_tokens


def test_remove_expired_tokens(expired_project_owner_access_token, now):
    with db_session:
        expired_tokens_exist = Token.exists(lambda token: token.expires <= now)
    assert expired_tokens_exist

    remove_expired_tokens.apply()

    with db_session:
        expired_tokens_exist = Token.exists(lambda token: token.expires <= now)

    assert not expired_tokens_exist
