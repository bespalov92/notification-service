from functools import lru_cache
from typing import Literal

from pydantic import AmqpDsn, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="NOTIFICATION_",
        extra="ignore",
    )

    app_name: str = "Notification Service"

    environment: Literal["local", "test", "production"] = "local"

    debug: bool = False

    log_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="POSTGRES_",
        extra="ignore",
    )

    db_name: str = "db_name"
    user: str = "user"
    password: str = "password"
    host: str = "localhost"
    port: int = 5432

    @property
    def dsn(self) -> PostgresDsn:
        return PostgresDsn(
            f"postgresql+asyncpg://"
            f"{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.db_name}"
        )


class RabbitMQSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="RABBITMQ_",
        extra="ignore",
    )

    user: str = "user"
    password: str = "pass"
    host: str = "rabbitmq"
    port: int = 5672

    @property
    def dsn(self) -> AmqpDsn:
        return AmqpDsn(
            f"amqp://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/"
        )


class Settings:
    def __init__(self) -> None:
        self.application = ApplicationSettings()
        self.postgres = PostgresSettings()
        self.rabbitmq = RabbitMQSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
