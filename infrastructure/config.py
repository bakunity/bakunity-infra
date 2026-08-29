from enum import StrEnum
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    """Typed runtime configuration loaded from environment without hard-coded secrets."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="BAKUNITY_",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="Bakunity Infra", min_length=1, max_length=100)
    app_env: AppEnvironment = AppEnvironment.DEVELOPMENT
    log_level: LogLevel = "INFO"
    request_id_header: str = Field(default="X-Request-ID", min_length=1, max_length=64)
    telegram_bot_token: SecretStr | None = None

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: object) -> object:
        if isinstance(value, str):
            return value.upper()
        return value

    @property
    def is_production_like(self) -> bool:
        return self.app_env in {AppEnvironment.STAGING, AppEnvironment.PRODUCTION}


@lru_cache
def get_settings() -> Settings:
    return Settings()
