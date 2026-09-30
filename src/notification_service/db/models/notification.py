from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    SmallInteger,
    String,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from notification_service.db.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    __table_args__ = (
        CheckConstraint(
            "attempts_count >= 0",
            name="ck_notifications_attempts_count_non_negative",
        ),
        CheckConstraint(
            "max_attempts > 0",
            name="ck_notifications_max_attempts_positive",
        ),
        Index(
            "ix_notifications_queue_order",
            "priority",
            "created_at",
            postgresql_where=text("status = 'queued'"),
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid7,
    )

    channel: Mapped[str] = mapped_column(String(32))

    priority: Mapped[int] = mapped_column(
        SmallInteger,
        default=5,
        server_default=text("5"),
    )

    status: Mapped[str] = mapped_column(
        String(32),
        default="queued",
        server_default=text("'queued'"),
    )

    payload: Mapped[dict[str, object]] = mapped_column(JSONB)

    idempotency_key: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
    )

    attempts_count: Mapped[int] = mapped_column(
        SmallInteger,
        default=0,
        server_default=text("0"),
    )

    max_attempts: Mapped[int] = mapped_column(
        SmallInteger,
        default=3,
        server_default=text("3"),
    )

    next_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    dead_lettered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
