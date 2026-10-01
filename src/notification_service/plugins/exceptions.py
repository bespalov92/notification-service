from notification_service.domain.enums import NotificationChannel
from notification_service.exceptions import NotificationServiceError


class InvalidPayloadError(NotificationServiceError):
    """
    Raised when the provided payload does not match
    the specific plugin requirements
    """
    ...


class PluginAlreadyRegisteredError(NotificationServiceError):
    """
    Raised when attempting to register a duplicate plugin
    for the same channel
    """

    def __init__(self, channel: NotificationChannel) -> None:
        self.channel = channel
        super().__init__(f"Plugin already registered for channel: {channel}")


class PluginNotFoundError(NotificationServiceError):
    """Raised when no registered plugin is found for the specified channel."""

    def __init__(self, channel: NotificationChannel) -> None:
        self.channel = channel
        super().__init__(f"No plugin registered for channel: {channel}")
