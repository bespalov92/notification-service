from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from notification_service.db.base import Base


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    __table_args__ = (
        Index(
            "ix_outbox_events_unpublished",
            "available_at",
            "created_at",
            postgresql_where=text(
                "published_at IS NULL"
            ),
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

    available_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
