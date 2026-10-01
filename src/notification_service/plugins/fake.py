from notification_service.domain.enums import NotificationChannel
from notification_service.plugins.errors import InvalidPayloadError


class FakePlugin:
    """
    A fake notification plugin implementation
    for testing and development purposes
    """
    def __init__(
        self,
        channel: NotificationChannel,
        provider_name: str = "fake",
    ) -> None:
        self.channel = channel
        self.provider_name = provider_name

    def validate(self, payload: dict[str, object]) -> None:
        message = payload.get("message")

        if not isinstance(message, str) or not message.strip():
            raise InvalidPayloadError(
                "payload.message must be a non-empty string"
            )

        if (
            self.channel is not NotificationChannel.EMAIL
            and "attachments" in payload
        ):
            raise InvalidPayloadError(
                "payload.attachments is only allowed for email"
            )
