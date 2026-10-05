from notification_service.domain.enums import NotificationChannel
from notification_service.plugins.fake import FakePlugin


async def test_fake_plugin_saves_sent_payload() -> None:
    plugin = FakePlugin(NotificationChannel.EMAIL)
    payload: dict[str, object] = {"message": "hello"}

    await plugin.send(payload)

    assert plugin.sent_payloads == [{"message": "hello"}]
