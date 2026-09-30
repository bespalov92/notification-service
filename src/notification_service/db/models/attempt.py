from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from notification_service.db.base import Base


class Attempt(Base):
    __tablename__ = "attempts"

    __table_args__ = (
        Index(
            "ix_attempts_notification_created",
            "notification_id",
            "created_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid7,
    )

    notification_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "notifications.id",
            ondelete="CASCADE",
        ),
    )

    channel: Mapped[str] = mapped_column(String(32))

    provider: Mapped[str] = mapped_column(String(100))

    status: Mapped[str] = mapped_column(String(32))

    retryable: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
    )

    response: Mapped[dict[str, object] | None] = mapped_column(JSONB)

    error: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
