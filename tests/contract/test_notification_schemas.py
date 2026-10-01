from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from pydantic import ValidationError

from notification_service.api.schemas.common import ApiError, ApiResponse
from notification_service.api.schemas.notifications import (
    CreateNotificationRequest,
    NotificationResponse,
)
from notification_service.domain.enums import (
    NotificationChannel,
    NotificationStatus,
)

VALID_REQUEST: dict[str, object] = {
    "channel": "email",
    "priority": 5,
    "ttl": "01:00:00",
    "idempotencyKey": "order-26-04-0001-notify-1",
    "payload": {
        "emails": ["user@example.com"],
        "subject": "Test",
        "message": "Hello",
    },
}


def test_create_notification_request_parses_api_contract() -> None:
    request = CreateNotificationRequest.model_validate(VALID_REQUEST)

    assert request.channel is NotificationChannel.EMAIL
    assert request.priority == 5
    assert request.ttl == timedelta(hours=1)
    assert request.idempotency_key == "order-26-04-0001-notify-1"

    serialized = request.model_dump(mode="json")

    assert serialized["idempotencyKey"] == (
        "order-26-04-0001-notify-1"
    )
    assert "idempotency_key" not in serialized


def test_create_notification_request_uses_defaults() -> None:
    request = CreateNotificationRequest.model_validate(
        {
            "channel": "sms",
            "payload": {
                "phone": "79990000000",
                "message": "Hello",
            },
        }
    )

    assert request.priority == 5
    assert request.ttl is None
    assert request.idempotency_key is None


def test_create_notification_request_rejects_unknown_channel() -> None:
    with pytest.raises(ValidationError):
        CreateNotificationRequest.model_validate(
            {
                **VALID_REQUEST,
                "channel": "fax",
            }
        )


@pytest.mark.parametrize("priority", [0, 6])
def test_create_notification_request_rejects_invalid_priority(
    priority: int,
) -> None:
    with pytest.raises(ValidationError):
        CreateNotificationRequest.model_validate(
            {
                **VALID_REQUEST,
                "priority": priority,
            }
        )


@pytest.mark.parametrize("ttl", ["00:00:00", "-00:00:01"])
def test_create_notification_request_rejects_invalid_ttl(
    ttl: str,
) -> None:
    with pytest.raises(ValidationError):
        CreateNotificationRequest.model_validate(
            {
                **VALID_REQUEST,
                "ttl": ttl,
            }
        )


@pytest.mark.parametrize(
    "idempotency_key",
    ["", "x" * 256],
)
def test_create_notification_request_rejects_invalid_key(
    idempotency_key: str,
) -> None:
    with pytest.raises(ValidationError):
        CreateNotificationRequest.model_validate(
            {
                **VALID_REQUEST,
                "idempotencyKey": idempotency_key,
            }
        )


def test_create_notification_request_rejects_empty_payload() -> None:
    with pytest.raises(ValidationError):
        CreateNotificationRequest.model_validate(
            {
                **VALID_REQUEST,
                "payload": {},
            }
        )


def test_create_notification_request_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        CreateNotificationRequest.model_validate(
            {
                **VALID_REQUEST,
                "maxAttempts": 10,
            }
        )


def test_success_response_uses_api_response() -> None:
    response = NotificationResponse(
        id=UUID("a3f1c2e0-4b2d-4e8a-9c1f-8d2e7b6a5c4d"),
        channel=NotificationChannel.EMAIL,
        status=NotificationStatus.QUEUED,
        created_at=datetime(2026, 9, 9, 8, 0, tzinfo=UTC),
    )

    api_response = ApiResponse[NotificationResponse](data=response)

    assert api_response.model_dump(mode="json") == {
        "data": {
            "id": "a3f1c2e0-4b2d-4e8a-9c1f-8d2e7b6a5c4d",
            "channel": "email",
            "status": "queued",
            "createdAt": "2026-09-09T08:00:00Z",
        },
        "meta": {},
        "error": None,
    }


def test_error_response_uses_api_response() -> None:
    api_response = ApiResponse[NotificationResponse](
        error=ApiError(
            code="validation_error",
            message="Request validation failed",
        ),
    )

    assert api_response.model_dump(mode="json") == {
        "data": None,
        "meta": {},
        "error": {
            "code": "validation_error",
            "message": "Request validation failed",
            "details": None,
        },
    }
