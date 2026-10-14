import asyncio
from uuid import UUID

from celery import Task

from notification_service.db.session import (
    dispose_database,
    session_maker,
)
from notification_service.domain.enums import NotificationChannel
from notification_service.messaging.celery_app import celery_app
from notification_service.plugins.fake import FakePlugin
from notification_service.plugins.registry import PluginRegistry
from notification_service.services.exceptions import RetryableDeliveryError
from notification_service.services.notification_delivery import (
    NotificationDeliveryService,
)
from notification_service.services.outbox_relay import OutboxRelayService


def build_plugin_registry() -> PluginRegistry:
    registry = PluginRegistry()

    for channel in NotificationChannel:
        registry.register(FakePlugin(channel))

    return registry


async def run_delivery(notification_id: UUID) -> None:
    try:
        async with session_maker() as session:
            service = NotificationDeliveryService(
                session=session,
                plugin_registry=build_plugin_registry(),
            )
            await service.deliver(notification_id)
    finally:
        await dispose_database()


@celery_app.task(
    bind=True,
    max_retries=None,
    name="notification_service.messaging.deliver_notification"
)
def deliver_notification(self: Task[..., None], notification_id: str) -> None:
    try:
        asyncio.run(run_delivery(UUID(notification_id)))
    except RetryableDeliveryError as error:
        raise self.retry(exc=error, countdown=5) from error


async def publish_delivery_task(notification_id: UUID) -> None:
    await asyncio.to_thread(
        deliver_notification.delay,
        str(notification_id),
    )


async def run_outbox_relay() -> int:
    try:
        async with session_maker() as session:
            service = OutboxRelayService(
                session=session,
                publish_notification=publish_delivery_task,
            )
            return await service.publish_events()
    finally:
        await dispose_database()


@celery_app.task(
    name="notification_service.messaging.publish_outbox_events"
)
def publish_outbox_events() -> int:
    return asyncio.run(run_outbox_relay())


@celery_app.task(name="notification_service.messaging.healthcheck")
def healthcheck() -> str:
    return "ok"
