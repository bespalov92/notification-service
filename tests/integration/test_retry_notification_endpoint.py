from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.notification import Notification
from notification_service.db.repositories.notification import (
    NotificationRepository,
)
from notification_service.domain.enums import (
    NotificationChannel,
    NotificationStatus,
)


def create_notification(status: str) -> Notification:
    return Notification(
        channel=NotificationChannel.EMAIL.value,
        payload={"message": "Retry me!"},
        idempotency_key=f"retry-{uuid4()}",
        status=status
    )


async def test_retry_failed_notification(
    db_session: AsyncSession,
    api_client: AsyncClient
) -> None:
    notification = create_notification(status=NotificationStatus.FAILED.value)
    repository = NotificationRepository(db_session)
    async with db_session.begin():
        await repository.add(notification)
    notification_id = notification.id

    response = await api_client.post(
        f"/api/v1/notifications/failed/{notification_id}/retry"
    )

    assert response.status_code == 202

    response_body = response.json()
    assert response_body["data"]["id"] == str(notification_id)
    assert response_body["data"]["status"] == NotificationStatus.QUEUED.value


async def test_cannot_retry_non_failed_notification(
    db_session: AsyncSession,
    api_client: AsyncClient
) -> None:
    notification = create_notification(status=NotificationStatus.SENT.value)
    repository = NotificationRepository(db_session)
    async with db_session.begin():
        await repository.add(notification)
    notification_id = notification.id

    response = await api_client.post(
        f"/api/v1/notifications/failed/{notification_id}/retry"
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == (
        "notification_cannot_be_retried"
    )


async def test_retry_non_existed_notification_returns_not_found(
    api_client: AsyncClient
) -> None:
    non_existed_id = uuid4()

    response = await api_client.post(
        f"/api/v1/notifications/failed/{non_existed_id}/retry"
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "notification_not_found"
