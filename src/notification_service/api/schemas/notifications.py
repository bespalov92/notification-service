from datetime import datetime, timedelta
from uuid import UUID

from pydantic import ConfigDict, Field

from notification_service.api.schemas.common import ApiSchema
from notification_service.domain.enums import (
    NotificationChannel,
    NotificationStatus,
)


class CreateNotificationRequest(ApiSchema):
    channel: NotificationChannel = Field(
        description="Channel used to deliver the notification",
        examples=["email", "sms", "push"]
    )

    priority: int = Field(
        default=5,
        ge=1,
        le=5,
        description=(
            "Notification priority from 1 (highest) to 5 (lowest)"
        ),
    )

    ttl: timedelta | None = Field(
        default=None,
        gt=timedelta(0),
        description="Optional notification lifetime in the queue",
    )

    idempotency_key: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Optional key used to prevent duplicate delivery",
    )

    payload: dict[str, object] = Field(
        min_length=1,
        description="Channel-specific notification data",
    )


class NotificationResponse(ApiSchema):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        description="Unique notification identifier",
    )

    channel: NotificationChannel = Field(
        description="Channel used to deliver the notification",
        examples=["email", "sms", "push"]
    )

    status: NotificationStatus = Field(
        description="Current notification status",
        examples=["queued", "sent"]
    )

    created_at: datetime = Field(
        description="Date and time when the notification was created",
    )
