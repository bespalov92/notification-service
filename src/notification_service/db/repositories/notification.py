from uuid import UUID

from sqlalchemy import select
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

