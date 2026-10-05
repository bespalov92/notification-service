from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.notification import Notification
from notification_service.db.models.outbox_event import OutboxEvent
from notification_service.db.repositories.notification import (
    NotificationRepository,
)
from notification_service.db.repositories.outbox_event import (
    OutboxEventRepository,
)
from notification_service.services.outbox_relay import (
    OutboxRelayService,
)


class PublishError(Exception):
    pass


async def _create_event(
    db_session: AsyncSession
) -> tuple[Notification, OutboxEvent]:
    notification_repository = NotificationRepository(db_session)
    outbox_repository = OutboxEventRepository(db_session)

    async with db_session.begin():
        notification = Notification(
            channel="email",
            payload={"message": "Hello"},
            idempotency_key=f"relay-{uuid4()}",
        )
        await notification_repository.add(notification)

        event = OutboxEvent(
            notification_id=notification.id,
            available_at=datetime(2026, 10, 4, tzinfo=UTC),
        )
        await outbox_repository.add(event)

    return notification, event


async def test_publish_events_marks_event_as_published(
    db_session: AsyncSession
) -> None:
    notification, event = await _create_event(db_session)
    published_notification_ids: list[UUID] = []

    async def publish_notification(notification_id: UUID) -> None:
        assert not db_session.in_transaction()
        published_notification_ids.append(notification_id)

    service = OutboxRelayService(
        session=db_session,
        publish_notification=publish_notification
    )

    await service.publish_events(limit=10)
    await db_session.refresh(event)

    assert notification.id in published_notification_ids
    assert event.published_at is not None
    assert event.locked_until is None


async def test_publish_events_keeps_event_on_publish_error(
    db_session: AsyncSession
) -> None:
    notification, event = await _create_event(db_session)

    async def publish_notification(notification_id: UUID) -> None:
        assert not db_session.in_transaction()
        if notification_id == notification.id:
            raise PublishError()

    service = OutboxRelayService(
        session=db_session,
        publish_notification=publish_notification
    )

    with pytest.raises(PublishError):
        await service.publish_events(limit=10)

    await db_session.refresh(event)

    assert event.published_at is None
    assert event.locked_until is not None
