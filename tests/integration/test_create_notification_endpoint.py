from collections.abc import AsyncGenerator
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.outbox_event import OutboxEvent
from notification_service.db.session import get_session
from notification_service.main import app


async def test_create_notification_endpoint(
    db_session: AsyncSession
) -> None:
    async def override_get_session() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)

    request_body = {
        "channel": "email",
        "priority": 2,
        "ttl": "01:00:00",
        "idempotencyKey": f"api-{uuid4()}",
        "payload": {
            "message": "Hello",
        }
    }

    try:
        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/notifications",
                json=request_body
            )
    finally:
        app.dependency_overrides.clear()

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
