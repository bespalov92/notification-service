from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.notification import Notification
from notification_service.db.models.outbox_event import OutboxEvent
from notification_service.db.repositories.notification import (
    NotificationRepository,
)
from notification_service.db.repositories.outbox_event import (
    OutboxEventRepository,
)


async def _create_notification(
    db_session: AsyncSession,
) -> Notification:
    repository = NotificationRepository(db_session)

    notification = Notification(
        channel="email",
        payload={"message": "Hello"},
        idempotency_key=f"outbox-{uuid4()}",
    )

    await repository.add(notification)

    return notification


async def test_add_outbox_event(
    db_session: AsyncSession,
) -> None:
    notification = await _create_notification(db_session)
    repository = OutboxEventRepository(db_session)

    event = OutboxEvent(
        notification_id=notification.id,
    )

    await repository.add(event)

    event_id = event.id
    db_session.expunge(event)

    statement = select(OutboxEvent).where(
        OutboxEvent.id == event_id,
    )
    stored_event = await db_session.scalar(statement)

    assert stored_event is not None
    assert stored_event.notification_id == notification.id
    assert stored_event.available_at is not None
    assert stored_event.published_at is None
    assert stored_event.locked_until is None


async def test_get_unpublished_events_returns_ready_events(
    db_session: AsyncSession,
) -> None:
    notification = await _create_notification(db_session)
    repository = OutboxEventRepository(db_session)
    now = datetime.now(UTC)

    first_ready_event = OutboxEvent(
        notification_id=notification.id,
        available_at=now - timedelta(minutes=2),
    )
    second_ready_event = OutboxEvent(
        notification_id=notification.id,
        available_at=now - timedelta(minutes=1),
    )
    future_event = OutboxEvent(
        notification_id=notification.id,
        available_at=now + timedelta(days=1),
    )
    published_event = OutboxEvent(
        notification_id=notification.id,
        available_at=now - timedelta(minutes=3),
        published_at=now,
    )
    active_lease_event = OutboxEvent(
        notification_id=notification.id,
        available_at=now - timedelta(minutes=5),
        locked_until=now + timedelta(minutes=5),
    )
    expired_lease_event = OutboxEvent(
        notification_id=notification.id,
        available_at=now - timedelta(minutes=3),
        locked_until=now - timedelta(minutes=1),
    )

    for event in (
        first_ready_event,
        second_ready_event,
        future_event,
        published_event,
        active_lease_event,
        expired_lease_event
    ):
        await repository.add(event)

    events = await repository.get_unpublished_events(
        limit=1000,
        lease_duration=timedelta(minutes=5)
    )

    notification_events = [
        event
        for event in events
        if event.notification_id == notification.id
    ]

    assert [event.id for event in notification_events] == [
        expired_lease_event.id,
        first_ready_event.id,
        second_ready_event.id,
    ]

    for event in notification_events:
        assert event.locked_until is not None


async def test_mark_published(
    db_session: AsyncSession,
) -> None:
    notification = await _create_notification(db_session)
    repository = OutboxEventRepository(db_session)

    event = OutboxEvent(
        notification_id=notification.id,
    )
    await repository.add(event)

    await repository.mark_published(event)

    event_id = event.id
    published_at = event.published_at
    db_session.expunge(event)

    stored_event = await db_session.get(
        OutboxEvent,
        event_id,
    )

    assert stored_event is not None
    assert stored_event.published_at == published_at
    assert stored_event.locked_until is None
