import asyncio
from uuid import UUID

from notification_service.db.session import (
    dispose_database,
    session_maker,
)
from notification_service.domain.enums import NotificationChannel
from notification_service.messaging.celery_app import celery_app
from notification_service.plugins.fake import FakePlugin
from notification_service.plugins.registry import PluginRegistry
from notification_service.services.notification_delivery import (
    NotificationDeliveryService,
)


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
    name="notification_service.messaging.deliver_notification"
)
def deliver_notification(notification_id: str) -> None:
    asyncio.run(run_delivery(UUID(notification_id)))


@celery_app.task(name="notification_service.messaging.healthcheck")
def healthcheck() -> str:
    return "ok"
