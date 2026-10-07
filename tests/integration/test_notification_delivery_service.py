from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.attempt import Attempt
from notification_service.db.models.notification import Notification
from notification_service.db.repositories.notification import (
    NotificationRepository,
)
from notification_service.domain.enums import (
    AttemptStatus,
    NotificationChannel,
    NotificationStatus,
)
from notification_service.plugins.fake import FakePlugin
from notification_service.plugins.registry import PluginRegistry
from notification_service.services.notification_delivery import (
    NotificationDeliveryService,
)


async def test_deliver_notification(db_session: AsyncSession) -> None:
    notification = Notification(
        channel=NotificationChannel.EMAIL.value,
        payload={"message": "Hello"},
        idempotency_key=f"delivery-{uuid4()}",
    )

    async with db_session.begin():
        repository = NotificationRepository(db_session)
        await repository.add(notification)

    plugin = FakePlugin(NotificationChannel.EMAIL)
    plugin_registry = PluginRegistry()
    plugin_registry.register(plugin)

    service = NotificationDeliveryService(
        session=db_session,
        plugin_registry=plugin_registry
    )

    result = await service.deliver(notification.id)

    assert result.status == NotificationStatus.SENT.value
    assert result.attempts_count == 1
    assert plugin.sent_payloads == [{"message": "Hello"}]

    stmt = select(Attempt).where(Attempt.notification_id == notification.id)
    attempt = await db_session.scalar(stmt)

    assert attempt is not None
    assert attempt.channel == NotificationChannel.EMAIL.value
    assert attempt.provider == "fake"
    assert attempt.status == AttemptStatus.SENT.value
