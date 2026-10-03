from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.outbox_event import OutboxEvent


async def test_create_notification_endpoint(
    api_client: AsyncClient,
    db_session: AsyncSession
) -> None:
    request_body = {
        "channel": "email",
        "priority": 2,
        "ttl": "01:00:00",
        "idempotencyKey": f"api-{uuid4()}",
        "payload": {
            "message": "Hello",
        }
    }

    response = await api_client.post(
        "/api/v1/notifications",
        json=request_body
    )

    assert response.status_code == 202

    response_body = response.json()

    assert response_body["data"]["channel"] == "email"
    assert response_body["data"]["status"] == "queued"
    assert response_body["data"]["createdAt"] is not None
    assert response_body["meta"] == {}
    assert response_body["error"] is None

    stmt = select(OutboxEvent).where(
        OutboxEvent.notification_id == response_body["data"]["id"])
    stored_event = await db_session.scalar(stmt)

    assert stored_event is not None
