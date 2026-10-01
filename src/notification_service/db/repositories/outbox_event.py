from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.outbox_event import OutboxEvent


class OutboxEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, event: OutboxEvent) -> None:
        self._session.add(event)
        await self._session.flush()
