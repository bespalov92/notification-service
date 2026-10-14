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
        "notification_service.messaging.deliver_notification": {
            "queue": "notifications",
        },
        "notification_service.messaging.publish_outbox_events": {
            "queue": "notifications",
        },
    },
    beat_schedule={
        "publish-outbox-events": {
            "task": (
                "notification_service.messaging.publish_outbox_events"
            ),
            "schedule": 1.0,
        },
    },
)
