from uuid import UUID, uuid4

from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.notification import Notification
from notification_service.domain.enums import NotificationStatus


async def test_clear_notification_queue(
    api_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    created_ids: list[UUID] = []

    for number in range(3):
        response = await api_client.post(
            "/api/v1/notifications",
            json={
                "channel": "email",
                "idempotencyKey": f"clear-{number}-{uuid4()}",
                "payload": {"message": f"Message {number}"},
            },
        )

        assert response.status_code == 202
        created_ids.append(UUID(response.json()["data"]["id"]))

    async with db_session.begin():
        sent_notification = await db_session.get(
            Notification,
            created_ids[-1],
        )
        assert sent_notification is not None

        sent_notification.status = NotificationStatus.SENT.value
        await db_session.flush()

        queued_before = await db_session.scalar(
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.status
                == NotificationStatus.QUEUED.value
            )
        )

    response = await api_client.delete("/api/v1/notifications")

    assert response.status_code == 200
    assert response.json()["data"]["cancelledCount"] == queued_before

    async with db_session.begin():
        queued_after = await db_session.scalar(
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.status
                == NotificationStatus.QUEUED.value
            )
        )
        sent_notification = await db_session.get(
            Notification,
            created_ids[-1],
        )

    assert queued_after == 0
    assert sent_notification is not None
    assert sent_notification.status == NotificationStatus.SENT.value
