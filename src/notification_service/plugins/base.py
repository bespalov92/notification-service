from typing import Protocol

from notification_service.domain.enums import NotificationChannel


class NotificationPlugin(Protocol):
    channel: NotificationChannel
    provider_name: str

    def validate(self, payload: dict[str, object]) -> None:
        pass

    async def send(self) -> None:
        pass
