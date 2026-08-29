from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment without hard-coded secrets."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="BAKUNITY_",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Bakunity Infra"
    app_env: str = "development"
    log_level: str = "INFO"
    telegram_bot_token: SecretStr | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
