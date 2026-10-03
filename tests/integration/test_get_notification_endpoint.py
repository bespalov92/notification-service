from uuid import uuid4

from httpx import AsyncClient


async def test_get_notification(
    api_client: AsyncClient
) -> None:
    create_response = await api_client.post(
        "/api/v1/notifications",
        json={
            "channel": "email",
            "idempotencyKey": f"get-{uuid4()}",
            "payload": {
                "message": "Hello",
            },
        },
    )

    created_notification = create_response.json()["data"]

    response = await api_client.get(
        f"/api/v1/notifications/{created_notification['id']}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "data": created_notification,
        "meta": {},
        "error": None,
    }


async def test_get_unknown_notification_returns_404(
    api_client: AsyncClient
) -> None:
    notification_id = uuid4()
    response = await api_client.get(
        f"/api/v1/notifications/{notification_id}"
    )

    assert response.status_code == 404
    assert response.json() == {
        "data": None,
        "meta": {},
        "error": {
            "code": "notification_not_found",
            "message": f"Notification {notification_id} not found",
            "details": None,
        },
    }
