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
    )

    status: NotificationStatus = Field(
        description="Current notification status",
    )

    created_at: datetime = Field(
        description="Date and time when the notification was created",
    )


class NotificationListParams(ApiSchema):
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of notifications to return",
    )

    offset: int = Field(
        default=0,
        ge=0,
        description="Number of notifications to skip",
    )

    channel: NotificationChannel | None = Field(
        default=None,
        description="Filter by delivery channel",
    )

    status: NotificationStatus | None = Field(
        default=None,
        description="Filter by current status",
    )

    created_from: datetime | None = Field(
        default=None,
        description="Created at or after this time",
    )

    created_to: datetime | None = Field(
        default=None,
        description="Created at or before this time",
    )


class ClearQueueResponse(ApiSchema):
    cancelled_count: int = Field(
        ge=0,
        description="Number of cancelled queued notifications",
    )
