from datetime import UTC, datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.outbox_event import OutboxEvent


class OutboxEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, event: OutboxEvent) -> None:
        self._session.add(event)
        await self._session.flush()

    async def get_unpublished_events(
        self,
        *,
        limit: int,
        lease_duration: timedelta
    ) -> list[OutboxEvent]:
        now = datetime.now(UTC)
        locked_until = now + lease_duration

        stmt = (
            select(OutboxEvent)
            .where(
                OutboxEvent.published_at.is_(None),
                OutboxEvent.available_at <= now,
                or_(
                    OutboxEvent.locked_until.is_(None),
                    OutboxEvent.locked_until <= now
                )
            )
            .order_by(
                OutboxEvent.available_at,
                OutboxEvent.created_at
            )
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        result = await self._session.scalars(stmt)
        events = list(result.all())

        for event in events:
            event.locked_until = locked_until

        await self._session.flush()

        return events

    async def mark_published(self, event: OutboxEvent) -> None:
        event.published_at = datetime.now(UTC)
        event.locked_until = None

        await self._session.flush()
