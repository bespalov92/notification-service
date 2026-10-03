from collections.abc import AsyncGenerator
from uuid import uuid4

from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.notification import Notification
from notification_service.db.session import get_session
from notification_service.main import app


async def post_notification(
    db_session: AsyncSession,
    request_body: dict[str, object],
) -> Response:
    async def override_get_session() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            return await client.post(
                "/api/v1/notifications",
                json=request_body,
            )
    finally:
        app.dependency_overrides.clear()


async def test_error_for_invalid_request(
    db_session: AsyncSession,
) -> None:
    request_body: dict[str, object] = {
        "channel": "email",
        "priority": 10,
        "payload": {
            "message": "Hello",
        },
    }

    response = await post_notification(db_session, request_body)

    assert response.status_code == 422

    response_body = response.json()

    assert response_body["data"] is None
    assert response_body["meta"] == {}
    assert response_body["error"]["code"] == "validation_error"
    assert response_body["error"]["message"] == "Request validation failed"

    details = response_body["error"]["details"]

    assert details is not None
    assert ["body", "priority"] in [detail["loc"] for detail in details]


async def test_error_for_invalid_plugin_payload(
    db_session: AsyncSession,
) -> None:
    idempotency_key = f"api-{uuid4()}"
    request_body: dict[str, object] = {
        "channel": "sms",
        "idempotencyKey": idempotency_key,
        "payload": {
            "message": "Hello",
            "attachments": ["invoice.pdf"],
        },
    }

    response = await post_notification(db_session, request_body)

    assert response.status_code == 422
    assert response.json() == {
        "data": None,
        "meta": {},
        "error": {
            "code": "invalid_payload",
            "message": (
                "payload.attachments is only allowed for email"
            ),
            "details": None,
        },
    }

    stmt = select(Notification).where(
        Notification.idempotency_key == idempotency_key
    )
    stored_notification = await db_session.scalar(stmt)

    assert stored_notification is None
