from notification_service.domain.enums import NotificationChannel
from notification_service.plugins.exceptions import InvalidPayloadError


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
        self.sent_payloads: list[dict[str, object]] = []

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

    async def send(self, payload: dict[str, object]) -> None:
        self.sent_payloads.append(payload.copy())
