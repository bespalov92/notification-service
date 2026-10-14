
from uuid import uuid4

from httpx import AsyncClient


async def test_list_notifications(api_client: AsyncClient) -> None:
    created_ids: set[str] = set()

    for number in range(2):
        response = await api_client.post(
            "/api/v1/notifications",
            json={
                "channel": "email",
                "idempotencyKey": f"list-{number}-{uuid4()}",
                "payload": {
                    "message": f"Message {number}",
                },
            },
        )

        assert response.status_code == 202
        created_ids.add(response.json()["data"]["id"])

    response = await api_client.get(
        "/api/v1/notifications",
        params={
            "limit": 100,
            "offset": 0,
        },
    )

    assert response.status_code == 200

    body = response.json()
    returned_ids = {
        notification["id"]
        for notification in body["data"]
    }

    assert created_ids <= returned_ids
    assert body["meta"]["limit"] == 100
    assert body["meta"]["offset"] == 0
    assert body["meta"]["total"] >= 2
    assert body["error"] is None


async def test_list_notifications_applies_filters(
    api_client: AsyncClient,
) -> None:
    email_response = await api_client.post(
        "/api/v1/notifications",
        json={
            "channel": "email",
            "idempotencyKey": f"filtered-email-{uuid4()}",
            "payload": {"message": "Email message"},
        },
    )
    sms_response = await api_client.post(
        "/api/v1/notifications",
        json={
            "channel": "sms",
            "idempotencyKey": f"filtered-sms-{uuid4()}",
            "payload": {"message": "SMS message"},
        },
    )

    assert email_response.status_code == 202
    assert sms_response.status_code == 202

    email_data = email_response.json()["data"]
    sms_data = sms_response.json()["data"]

    response = await api_client.get(
        "/api/v1/notifications",
        params={
            "channel": "email",
            "status": "queued",
            "createdFrom": email_data["createdAt"],
            "createdTo": sms_data["createdAt"],
            "limit": 100,
        },
    )

    assert response.status_code == 200

    body = response.json()
    returned_ids = {
        notification["id"]
        for notification in body["data"]
    }

    assert email_data["id"] in returned_ids
    assert sms_data["id"] not in returned_ids
    assert body["meta"]["total"] == 1
