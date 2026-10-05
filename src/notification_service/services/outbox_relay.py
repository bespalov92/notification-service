from collections.abc import Awaitable, Callable
from datetime import timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.repositories.outbox_event import (
    OutboxEventRepository,
)

NotificationPublisher = Callable[[UUID], Awaitable[None]]

class OutboxRelayService:
    def __init__(
        self,
        session: AsyncSession,
        publish_notification: NotificationPublisher,
        lease_duration: timedelta = timedelta(seconds=60)
    ) -> None:
        self._session = session
        self._publish_notification = publish_notification
        self._lease_duration = lease_duration
        self._repository = OutboxEventRepository(session)

    async def publish_events(self, *, limit: int = 100) -> int:
        async with self._session.begin():
            events = await self._repository.get_unpublished_events(
                limit=limit,
                lease_duration=self._lease_duration
            )

        published_count = 0

        for event in events:
            await self._publish_notification(event.notification_id)

            async with self._session.begin():
                await self._repository.mark_published(event)

            published_count += 1

        return published_count
