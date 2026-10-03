from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.notification import Notification
from notification_service.db.repositories.notification import (
    NotificationRepository,
)


def create_notification(
    *,
    idempotency_key: str | None = None,
    attempts_count: int = 0,
    max_attempts: int = 3,
) -> Notification:
    return Notification(
        channel="email",
        payload={"recipient": "user@example.com"},
        idempotency_key=idempotency_key,
        attempts_count=attempts_count,
        max_attempts=max_attempts,
    )


async def test_idempotency_key_must_be_unique(
    db_session: AsyncSession,
) -> None:
    repository = NotificationRepository(db_session)
    idempotency_key = f"duplicate-{uuid4()}"

    first_notification = create_notification(idempotency_key=idempotency_key)
    second_notification = create_notification(idempotency_key=idempotency_key)

    await repository.add(first_notification)

    with pytest.raises(IntegrityError):
        await repository.add(second_notification)


async def test_attempts_count_cannot_be_negative(
    db_session: AsyncSession,
) -> None:
    repository = NotificationRepository(db_session)
    notification = create_notification(attempts_count=-1)

    with pytest.raises(IntegrityError):
        await repository.add(notification)


async def test_max_attempts_must_be_positive(
    db_session: AsyncSession,
) -> None:
    repository = NotificationRepository(db_session)
    notification = create_notification(max_attempts=0)

    with pytest.raises(IntegrityError):
        await repository.add(notification)
