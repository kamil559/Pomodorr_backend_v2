from celery import Celery
from celery.schedules import crontab
from flask import Flask
from kombu import Queue

celery_instance = Celery("pomororo_system", include="web_app.celery_tasks")
celery_instance.config_from_object("web_app.celery.setup", namespace="CELERY")


def create_celery(app: Flask) -> Celery:
    class ContextTask(celery_instance.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_instance.Task = ContextTask  # noqa
    return celery_instance


celery_instance.conf.broker_transport_options = {"queue_order_strategy": "priority"}

celery_instance.conf.task_queues = (
    Queue(
        name="auth_tasks",
        routing_key="pomororo_system.web_app.celery_tasks.auth.#",
        queue_arguments={"x-max-priority": 1},
    ),
)

celery_instance.conf.beat_schedule = {
    "remove-expired-tokens-every-midnight": {
        "task": "pomororo_system.web_app.celery_tasks.auth.remove_expired_tokens",
        "schedule": crontab(hour=0, minute=0),
        "options": {"queue": "auth_tasks"},
    }
}
