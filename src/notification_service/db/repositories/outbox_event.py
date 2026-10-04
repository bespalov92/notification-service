from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.outbox_event import OutboxEvent


class OutboxEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, event: OutboxEvent) -> None:
        self._session.add(event)
        await self._session.flush()

    async def get_unpublished_events(self, limit: int) -> list[OutboxEvent]:
        stmt = (
            select(OutboxEvent)
            .where(
                OutboxEvent.published_at.is_(None),
                OutboxEvent.available_at <= func.now()
            )
            .order_by(
                OutboxEvent.available_at,
                OutboxEvent.created_at
            )
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        result = await self._session.scalars(stmt)

        return list(result.all())

    async def mark_published(self, event: OutboxEvent) -> None:
        event.published_at = datetime.now(UTC)
        await self._session.flush()
