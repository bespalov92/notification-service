from notification_service.domain.enums import NotificationChannel
from notification_service.exceptions import NotificationAppError


class InvalidPayloadError(NotificationAppError):
    """
    Raised when the provided payload does not match
    the specific plugin requirements
    """
    ...


class PluginNotFoundError(NotificationAppError):
    """Raised when no registered plugin is found for the specified channel."""

    def __init__(self, channel: NotificationChannel) -> None:
        self.channel = channel
        super().__init__(f"No plugin registered for channel: {channel}")
