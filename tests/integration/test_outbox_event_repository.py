from uuid import uuid4

import pytest
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


async def test_add_outbox_event(
    db_session: AsyncSession,
) -> None:
    notification_repository = NotificationRepository(db_session)
    outbox_repository = OutboxEventRepository(db_session)

    notification = Notification(
        channel="email",
        payload={"message": "Hello"},
        idempotency_key=f"outbox-{uuid4()}",
    )
    await notification_repository.add(notification)

    event = OutboxEvent(notification_id=notification.id)
    await outbox_repository.add(event)

    event_id = event.id
    db_session.expunge(event)

    stmt = select(OutboxEvent).where(OutboxEvent.id == event_id)
    stored_event = await db_session.scalar(stmt)

    assert stored_event is not None
    assert stored_event.notification_id == notification.id
    assert stored_event.available_at is not None
    assert stored_event.published_at is None
