from email.message import EmailMessage
from unittest.mock import AsyncMock

import pytest
from pytest import MonkeyPatch

from notification_service.config import SMTPSettings
from notification_service.plugins.email import EmailPlugin
from notification_service.plugins.exceptions import InvalidPayloadError


def create_plugin() -> EmailPlugin:
    return EmailPlugin(
        SMTPSettings(
            host="mailpit",
            port=1025,
            use_tls=False,
            start_tls=False,
        )
    )


def test_email_plugin_rejects_missing_recipients() -> None:
    plugin = create_plugin()

    with pytest.raises(InvalidPayloadError, match="emails"):
        plugin.validate({"message": "Hello"})


async def test_email_plugin_sends_message(
    monkeypatch: MonkeyPatch,
) -> None:
    send = AsyncMock(return_value=({}, "accepted"))
    monkeypatch.setattr(
        "notification_service.plugins.email.aiosmtplib.send",
        send,
    )

    plugin = create_plugin()

    await plugin.send(
        {
            "from": "sender@example.com",
            "emails": ["user@example.com"],
            "subject": "Test notification",
            "message": "Hello!"
        }
    )

    send.assert_awaited_once()

    call = send.await_args
    assert call is not None

    message = call.args[0]
    assert isinstance(message, EmailMessage)
    assert message["From"] == "sender@example.com"
    assert message["To"] == "user@example.com"
    assert message["Subject"] == "Test notification"
