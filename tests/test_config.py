import pytest
from pydantic import ValidationError

from infrastructure.config import AppEnvironment, Settings


def test_environment_is_typed() -> None:
    settings = Settings(app_env="staging")

    assert settings.app_env is AppEnvironment.STAGING
    assert settings.is_production_like is True


def test_log_level_is_normalized() -> None:
    settings = Settings(log_level="debug")

    assert settings.log_level == "DEBUG"


def test_invalid_environment_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="live")


def test_secret_value_is_redacted_from_settings_repr() -> None:
    settings = Settings(telegram_bot_token="do-not-log-this")

    assert "do-not-log-this" not in repr(settings)
