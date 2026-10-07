from uuid import uuid4

import pytest
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
from notification_service.plugins.exceptions import PluginSendError
from notification_service.plugins.fake import FakePlugin
from notification_service.plugins.registry import PluginRegistry
from notification_service.services.notification_delivery import (
    NotificationDeliveryService,
)


class FailingPlugin:
    channel: NotificationChannel = NotificationChannel.EMAIL
    provider_name: str = "failing"

    def __init__(self, *, retryable: bool) -> None:
        self._retryable = retryable

    def validate(self, payload: dict[str, object]) -> None:
        del payload

    async def send(self, payload: dict[str, object]) -> None:
        del payload

        raise PluginSendError(
            "Provider unavailable",
            retryable=self._retryable,
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


@pytest.mark.parametrize(
    ("retryable", "expected_status"),
    [
        (True, NotificationStatus.QUEUED.value),
        (False, NotificationStatus.FAILED.value),
    ],
)
async def test_deliver_records_failed_attempt(
    db_session: AsyncSession,
    retryable: bool,
    expected_status: str,
) -> None:
    notification = Notification(
        channel=NotificationChannel.EMAIL.value,
        payload={"message": "Hello"},
        idempotency_key=f"failed-delivery-{uuid4()}",
    )

    async with db_session.begin():
        repository = NotificationRepository(db_session)
        await repository.add(notification)

    plugin = FailingPlugin(retryable=retryable)
    plugin_registry = PluginRegistry()
    plugin_registry.register(plugin)

    service = NotificationDeliveryService(
        session=db_session,
        plugin_registry=plugin_registry,
    )

    with pytest.raises(
        PluginSendError,
        match="Provider unavailable",
    ):
        await service.deliver(notification.id)

    stored_notification = await db_session.scalar(
        select(Notification).where(
            Notification.id == notification.id
        )
    )

    assert stored_notification is not None
    assert stored_notification.status == expected_status
    assert stored_notification.attempts_count == 1

    attempt = await db_session.scalar(
        select(Attempt).where(
            Attempt.notification_id == notification.id
        )
    )

    assert attempt is not None
    assert attempt.provider == "failing"
    assert attempt.status == AttemptStatus.FAILED.value
    assert attempt.retryable is retryable
    assert attempt.error == "Provider unavailable"
