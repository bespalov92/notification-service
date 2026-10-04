from celery import Celery

from notification_service.config import get_settings

settings = get_settings()

celery_app = Celery(
    "notification_service",
    broker=str(settings.rabbitmq.dsn),
    include=["notification_service.messaging.tasks"],
)

celery_app.conf.update(
    broker_connection_retry_on_startup=True,
    task_default_queue="notifications",
    task_ignore_result=True,
    task_routes={
        "notification_service.messaging.healthcheck": {
            "queue": "notifications",
        },
    },
)
