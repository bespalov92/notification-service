from email.message import EmailMessage

import aiosmtplib
from aiosmtplib.errors import (
    SMTPAuthenticationError,
    SMTPException,
    SMTPRecipientsRefused,
)
from pydantic import BaseModel, ConfigDict, EmailStr, Field, ValidationError

from notification_service.config import SMTPSettings
from notification_service.domain.enums import NotificationChannel
from notification_service.plugins.exceptions import (
    InvalidPayloadError,
    PluginSendError,
)


class EmailPayload(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    from_email: EmailStr = Field(
        alias="from",
        description="Email address of the sender"
    )

    emails: list[EmailStr] = Field(
        min_length=1,
        description="Email addresses of the recipients"
    )

    subject: str = Field(
        default="Notification",
        min_length=1,
        description="Email subject"
    )

    message: str = Field(
        min_length=1,
        description="Plain-text email body"
    )

    attachments: list[str] | None = Field(
        description="Optional email attachments",
        default=None
    )


class EmailPlugin:
    channel = NotificationChannel.EMAIL
    provider_name = "smtp"

    def __init__(self, settings: SMTPSettings) -> None:
        self._settings = settings

    def validate(self, payload: dict[str, object]) -> None:
        try:
            EmailPayload.model_validate(payload)
        except ValidationError as error:
            raise InvalidPayloadError(
                f"Invalid email payload: {error}"
            ) from error

    async def send(self, payload: dict[str, object]) -> None:
        email_payload = EmailPayload.model_validate(payload)

        recipients = [
            str(email_address)
            for email_address in email_payload.emails
        ]

        message = EmailMessage()
        message["From"] = email_payload.from_email
        message["To"] = ", ".join(recipients)
        message["Subject"] = email_payload.subject
        message.set_content(email_payload.message)

        password = (
            self._settings.password.get_secret_value()
            if self._settings.password is not None
            else None
        )

        try:
            recipient_errors, _ = await aiosmtplib.send(
                message,
                hostname=self._settings.host,
                port=self._settings.port,
                username=self._settings.username,
                password=password,
                use_tls=self._settings.use_tls,
                start_tls=self._settings.start_tls,
                timeout=self._settings.timeout,
            )
        except SMTPAuthenticationError as error:
            raise PluginSendError(
                "SMTP authentication failed",
                retryable=False
            ) from error
        except SMTPRecipientsRefused as error:
            raise PluginSendError(
                "SMTP rejected all recipients",
                retryable=False,
            ) from error
        except (SMTPException, OSError) as error:
            raise PluginSendError(
                "SMTP provider is unavailable",
                retryable=True,
            ) from error

        if recipient_errors:
            rejected = ", ".join(recipient_errors)
            raise PluginSendError(
                f"SMTP rejected recipients: {rejected}",
                retryable=False
            )
