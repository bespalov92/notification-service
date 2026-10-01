from typing import Protocol

from notification_service.domain.enums import NotificationChannel


class NotificationPlugin(Protocol):
    channel: NotificationChannel
    provider_name: str

    def validate(self) -> None:
        pass

    async def send(self) -> None:
        pass
