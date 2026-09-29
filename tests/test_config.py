from pathlib import Path

from pydantic_settings import SettingsConfigDict
from pytest import MonkeyPatch

from notification_service.config import ApplicationSettings


class FakeApplicationSettings(ApplicationSettings):
    model_config = SettingsConfigDict(
        env_file=None,
        env_prefix="NOTIFICATION_",
        extra="ignore",
    )


def test_settings_have_local_defaults(
    monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.delenv("NOTIFICATION_APP_NAME", raising=False)

    settings = FakeApplicationSettings()

    assert settings.app_name == "Notification Service"


def test_environment_has_priority_over_dotenv(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "NOTIFICATION_APP_NAME=Name from dotenv\n"
        "NOTIFICATION_DEBUG=false\n",
        encoding="utf-8",
    )

    monkeypatch.setenv(
        "NOTIFICATION_APP_NAME",
        "FuzzBuzz",
    )
    monkeypatch.setenv("NOTIFICATION_DEBUG", "true")

    settings = FakeApplicationSettings()

    assert settings.app_name == "FuzzBuzz"
    assert settings.debug is True
