from pony.orm import db_session
from web_app.authentication.helpers import prune_expired_tokens
from web_app.celery import celery_app


@celery_app.task(name="pomororo_system.web_app.celery_tasks.auth.remove_expired_tokens")
def remove_expired_tokens() -> None:
    with db_session:
        prune_expired_tokens()
