from uuid import UUID, uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.notification import Notification
from notification_service.domain.enums import NotificationStatus


async def test_cancel_queued_notification(
    api_client: AsyncClient,
) -> None:
    create_response = await api_client.post(
        "/api/v1/notifications",
        json={
            "channel": "sms",
            "idempotencyKey": f"cancel-{uuid4()}",
            "payload": {"message": "Cancel me"},
        },
    )
    notification_id = create_response.json()["data"]["id"]

    response = await api_client.delete(
        f"/api/v1/notifications/{notification_id}"
    )

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "cancelled"

    repeated_response = await api_client.delete(
        f"/api/v1/notifications/{notification_id}"
    )

    assert repeated_response.status_code == 200
    assert repeated_response.json()["data"]["status"] == "cancelled"


async def test_cannot_cancel_sent_notification(
    api_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    create_response = await api_client.post(
        "/api/v1/notifications",
        json={
            "channel": "sms",
            "idempotencyKey": f"sent-{uuid4()}",
            "payload": {"message": "Already sent"},
        },
    )
    notification_id = UUID(create_response.json()["data"]["id"])

    async with db_session.begin():
        notification = await db_session.get(
            Notification,
            notification_id,
        )
        assert notification is not None
        notification.status = NotificationStatus.SENT.value

    response = await api_client.delete(
        f"/api/v1/notifications/{notification_id}"
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == (
        "notification_cannot_be_cancelled"
    )
