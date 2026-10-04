from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.notification import Notification
from notification_service.db.models.outbox_event import OutboxEvent
from notification_service.db.repositories.notification import (
    NotificationRepository,
)
from notification_service.db.repositories.outbox_event import (
    OutboxEventRepository,
)
from notification_service.domain.enums import NotificationChannel
from notification_service.plugins.registry import PluginRegistry
from notification_service.services.exceptions import NotificationNotFoundError


class NotificationService:
    def __init__(
        self,
        session: AsyncSession,
        plugin_registry: PluginRegistry
    ) -> None:
        self._session = session
        self._plugin_registry = plugin_registry
        self._notification_repository = NotificationRepository(session)
        self._outbox_repository = OutboxEventRepository(session)

    async def create(
        self,
        *,
        channel: NotificationChannel,
        priority: int,
        ttl: timedelta | None,
        idempotency_key: str | None,
        payload: dict[str, object],
    ) -> Notification:
        plugin = self._plugin_registry.get(channel)
        plugin.validate(payload)

        async with self._session.begin():
            existing_notification = None
            if idempotency_key:
                existing_notification = (
                    await self._notification_repository
                    .get_by_idempotency_key(idempotency_key)
                )
            if existing_notification is not None:
                return existing_notification

            expires_at = (
                datetime.now(UTC) + ttl
                if ttl is not None
                else None
            )

            notification = Notification(
                channel=channel.value,
                priority=priority,
                payload=payload,
                idempotency_key=idempotency_key,
                expires_at=expires_at,
            )
            await self._notification_repository.add(notification)

            event = OutboxEvent(notification_id = notification.id)
            await self._outbox_repository.add(event)

        return notification

    async def get_by_id(self, notification_id: UUID) -> Notification:
        notification = await self._notification_repository.get_by_id(
            notification_id
        )

        if notification is None:
            raise NotificationNotFoundError(notification_id)

        return notification
