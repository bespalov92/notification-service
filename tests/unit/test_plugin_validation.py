import pytest

from notification_service.domain.enums import NotificationChannel
from notification_service.plugins.exceptions import (
    InvalidPayloadError,
    PluginAlreadyRegisteredError,
    PluginNotFoundError,
)
from notification_service.plugins.fake import FakePlugin
from notification_service.plugins.registry import PluginRegistry


def test_registry_returns_plugin_by_channel() -> None:
    plugin = FakePlugin(NotificationChannel.EMAIL)

    registry = PluginRegistry()
    registry.register(plugin)

    result = registry.get(NotificationChannel.EMAIL)

    assert result is plugin
    assert result.provider_name == "fake"


def test_registry_rejects_duplicate_channel() -> None:
    first_plugin = FakePlugin(NotificationChannel.EMAIL)
    second_plugin = FakePlugin(NotificationChannel.EMAIL)

    registry = PluginRegistry()
    registry.register(first_plugin)

    with pytest.raises(PluginAlreadyRegisteredError, match="email"):
        registry.register(second_plugin)


def test_registry_raises_error_for_unknown_channel() -> None:
    registry = PluginRegistry()

    with pytest.raises(PluginNotFoundError) as error:
        registry.get(NotificationChannel.PUSH)

    assert error.value.channel is NotificationChannel.PUSH


def test_fake_email_plugin_accepts_valid_payload() -> None:
    plugin = FakePlugin(NotificationChannel.EMAIL)

    plugin.validate(
        {
            "message": "Hello",
            "attachments": ["smb://files/document.pdf"],
        }
    )


@pytest.mark.parametrize(
    "message",
    [None, "", "   ", 42],
)
def test_fake_plugin_rejects_invalid_message(
    message: object,
) -> None:
    plugin = FakePlugin(NotificationChannel.SMS)

    with pytest.raises(InvalidPayloadError, match="message"):
        plugin.validate({"message": message})


@pytest.mark.parametrize(
    "channel",
    [
        NotificationChannel.SMS,
        NotificationChannel.PUSH,
    ],
)
def test_fake_plugin_rejects_attachments_for_non_email(
    channel: NotificationChannel,
) -> None:
    plugin = FakePlugin(channel)

    with pytest.raises(InvalidPayloadError, match="attachments"):
        plugin.validate(
            {
                "message": "Hello",
                "attachments": ["smb://files/document.pdf"],
            }
        )
