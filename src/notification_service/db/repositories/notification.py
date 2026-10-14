from datetime import datetime
from uuid import UUID

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.notification import Notification
from notification_service.domain.enums import NotificationChannel, NotificationStatus


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, notification: Notification) -> None:
        self._session.add(notification)
        await self._session.flush()

    async def get_by_id(
        self,
        notification_id:  UUID,
    ) -> Notification | None:
        return await self._session.get(Notification, notification_id)

    async def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> Notification | None:
        stmt = select(Notification).where(
            Notification.idempotency_key == idempotency_key
        )

        return await self._session.scalar(stmt)

    async def get_page(
        self,
        *,
        limit: int,
        offset: int,
        channel: NotificationChannel | None,
        status: NotificationStatus | None,
        created_from: datetime | None,
        created_to: datetime | None,
    ) -> tuple[list[Notification], int]:
        filters: list[ColumnElement[bool]] = []

        if channel is not None:
            filters.append(Notification.channel == channel.value)

        if status is not None:
            filters.append(Notification.status == status.value)

        if created_from is not None:
            filters.append(Notification.created_at >= created_from)

        if created_to is not None:
            filters.append(Notification.created_at <= created_to)

        stmt = (
            select(Notification)
            .where(*filters)
            .order_by(
                Notification.created_at.desc(),
                Notification.id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        notifications = list(
            (await self._session.scalars(stmt)).all()
        )

        total = await self._session.scalar(
            select(func.count())
            .select_from(Notification)
            .where(*filters)
        )

        return notifications, total or 0
