from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.notification import Notification


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
        offset: int
    ) -> tuple[list[Notification], int]:
        stmt = (
            select(Notification)
            .order_by(
                Notification.created_at.desc(),
                Notification.id.desc()
            )
            .limit(limit)
            .offset(offset)
        )

        notifications = list((await self._session.scalars(stmt)).all())

        total = await self._session.scalar(
            select(func.count()).select_from(Notification)
        )

        return notifications, total or 0
