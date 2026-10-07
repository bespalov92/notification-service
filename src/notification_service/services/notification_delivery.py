from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.attempt import Attempt
from notification_service.db.models.notification import Notification
from notification_service.db.repositories.attempt import AttemptRepository
from notification_service.db.repositories.notification import NotificationRepository
from notification_service.domain.enums import AttemptStatus, NotificationChannel, NotificationStatus
from notification_service.plugins.registry import PluginRegistry
from notification_service.services.exceptions import NotificationNotFoundError


class NotificationDeliveryService:
    def __init__(
        self,
        session: AsyncSession,
        plugin_registry: PluginRegistry
    ) -> None:
        self._session = session
        self._plugin_registry = plugin_registry
        self._notification_repository = NotificationRepository(session)
        self._attempt_repository = AttemptRepository(session)

    async def deliver(self, notification_id: UUID) -> Notification:
        async with self._session.begin():
            notification = (
                await self._notification_repository.get_by_id(
                    notification_id
                )
            )

            if notification is None:
                raise NotificationNotFoundError(notification_id)

            channel = NotificationChannel(notification.channel)
            payload = notification.payload.copy()

        plugin = self._plugin_registry.get(channel)

        await plugin.send(payload)

        async with self._session.begin():
            notification.status = NotificationStatus.SENT.value
            notification.attempts_count += 1

            attempt = Attempt(
                notification_id=notification.id,
                channel=notification.channel,
                provider=plugin.provider_name,
                status=AttemptStatus.SENT.value,
            )
            await self._attempt_repository.add(attempt)

        return notification
