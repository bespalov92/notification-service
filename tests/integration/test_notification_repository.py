from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.notification import Notification
from notification_service.db.repositories.notification import (
    NotificationRepository,
)


def create_notification() -> Notification:
    return Notification(
        channel="email",
        payload={
            "recipient": "user@example.com",
            "subject": "Test notification",
        },
        idempotency_key=f"test-{uuid4()}",
    )


@pytest.mark.asyncio
async def test_add_and_get_notification_by_id(
    db_session: AsyncSession,
) ->  None:
    repository = NotificationRepository(db_session)
    notification = create_notification()

    await repository.add(notification)
    db_session.expunge(notification)

    stored_notification = await repository.get_by_id(notification.id)

    assert stored_notification is not None
    assert stored_notification.id == notification.id
    assert stored_notification.channel == "email"
    assert stored_notification.status == "queued"


@pytest.mark.asyncio
async def test_get_notification_by_idempotency_key(
    db_session: AsyncSession
) -> None:
    repository = NotificationRepository(db_session)
    notification = create_notification()

    assert notification.idempotency_key is not None

    await repository.add(notification)
    db_session.expunge(notification)

    stored_notification = await repository.get_by_idempotency_key(
        notification.idempotency_key
    )

    assert stored_notification is not None
    assert stored_notification.id == notification.id
