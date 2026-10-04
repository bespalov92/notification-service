from notification_service.messaging.celery_app import celery_app
from notification_service.messaging.tasks import healthcheck


def test_celery_uses_json_messages() -> None:
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.accept_content[0] == "json"


def test_celery_uses_notifications_queue() -> None:
    assert celery_app.conf.task_default_queue == "notifications"
    assert celery_app.conf.task_ignore_result is True


def test_healthcheck_task() -> None:
    assert healthcheck() == "ok"
