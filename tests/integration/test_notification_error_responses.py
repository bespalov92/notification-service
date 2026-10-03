from uuid import uuid4

from httpx import AsyncClient, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.notification import Notification


async def post_notification(
    api_client: AsyncClient,
    request_body: dict[str, object]
) -> Response:
    return await api_client.post(
        "/api/v1/notifications",
        json=request_body,
    )


async def test_error_for_invalid_request(
    api_client: AsyncClient
) -> None:
    request_body: dict[str, object] = {
        "channel": "email",
        "priority": 10,
        "payload": {
            "message": "Hello",
        },
    }

    response = await post_notification(api_client, request_body)

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
    api_client: AsyncClient,
    db_session: AsyncSession
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

    response = await post_notification(api_client, request_body)

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
