from notification_service.messaging.celery_app import celery_app


@celery_app.task(name="notification_service.messaging.healthcheck")
def healthcheck() -> str:
    return "ok"
