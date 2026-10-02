from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.notification import Notification
from notification_service.db.models.outbox_event import OutboxEvent
from notification_service.domain.enums import NotificationChannel
from notification_service.plugins.exceptions import InvalidPayloadError
from notification_service.plugins.fake import FakePlugin
from notification_service.plugins.registry import PluginRegistry
from notification_service.services.notification import NotificationService


def create_service(
    session: AsyncSession,
    channel: NotificationChannel,
) -> NotificationService:
    registry = PluginRegistry()
    registry.register(FakePlugin(channel))

    return NotificationService(session=session, plugin_registry=registry)


@pytest.mark.asyncio
async def test_create_notification_with_outbox_event(
    db_session: AsyncSession
) -> None:
    service = create_service(db_session, NotificationChannel.EMAIL)

    notification = await service.create(
        channel=NotificationChannel.EMAIL,
        priority=2,
        ttl=timedelta(hours=1),
        idempotency_key=f"create={uuid4()}",
        payload={"message": "hello"}
    )

    stmt = select(OutboxEvent).where(
        OutboxEvent.notification_id == notification.id
    )
    stored_event = await db_session.scalar(stmt)

    assert notification.channel == "email"
    assert notification.priority == 2
    assert notification.status == "queued"
    assert notification.expires_at is not None
    assert notification.expires_at > datetime.now(UTC)

    assert stored_event is not None
    assert stored_event.notification_id == notification.id


@pytest.mark.asyncio
async def test_idempotency_returns_existing_notification(
    db_session: AsyncSession,
) -> None:
    service = create_service(db_session, NotificationChannel.EMAIL)

    idempotency_key = f"idempotency-{uuid4()}"

    first = await service.create(
        channel=NotificationChannel.EMAIL,
        priority=5,
        ttl=None,
        idempotency_key=idempotency_key,
        payload={"message": "hello"},
    )
    second = await service.create(
        channel=NotificationChannel.EMAIL,
        priority=5,
        ttl=None,
        idempotency_key=idempotency_key,
        payload={"message": "hello"},
    )

    stmt = select(func.count(OutboxEvent.id)).where(
        OutboxEvent.notification_id == first.id,
    )
    events_count = await db_session.scalar(stmt)

    assert second.id == first.id
    assert events_count == 1


@pytest.mark.asyncio
async def test_invalid_payload_is_not_persisted(
    db_session: AsyncSession,
) -> None:
    service = create_service(
        db_session,
        NotificationChannel.SMS,
    )
    idempotency_key = f"invalid-{uuid4()}"

    with pytest.raises(InvalidPayloadError):
        await service.create(
            channel=NotificationChannel.SMS,
            priority=1,
            ttl=None,
            idempotency_key=idempotency_key,
            payload={
                "message": "Hello",
                "attachments": ["document.pdf"],
            },
        )

    stmt = select(Notification).where(
        Notification.idempotency_key == idempotency_key,
    )
    stored_notification = await db_session.scalar(stmt)

    assert stored_notification is None
