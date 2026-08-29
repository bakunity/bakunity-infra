from __future__ import annotations

import json
import logging
import re
from contextvars import ContextVar, Token
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from infrastructure.config import Settings

_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_request_id: ContextVar[str | None] = ContextVar("bakunity_request_id", default=None)


def new_request_id() -> str:
    return uuid4().hex


def normalize_request_id(value: str | None) -> str:
    """Accept a safe transport request id or generate a new opaque value."""
    if value and _REQUEST_ID_PATTERN.fullmatch(value):
        return value
    return new_request_id()


def set_request_id(value: str) -> Token[str | None]:
    return _request_id.set(value)


def reset_request_id(token: Token[str | None]) -> None:
    _request_id.reset(token)


def get_request_id() -> str | None:
    return _request_id.get()


class JsonLogFormatter(logging.Formatter):
    """Small stdlib JSON formatter with correlation context and no secret serialization."""

    _extra_fields = ("event", "method", "path", "status_code", "duration_ms")

    def __init__(self, *, service: str, environment: str) -> None:
        super().__init__()
        self.service = service
        self.environment = environment

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "service": self.service,
            "environment": self.environment,
            "message": record.getMessage(),
        }

        request_id = get_request_id()
        if request_id is not None:
            payload["request_id"] = request_id

        for field in self._extra_fields:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def configure_logging(settings: Settings) -> None:
    """Configure one process-wide structured stdout/stderr logging pipeline."""
    root = logging.getLogger()
    root.setLevel(settings.log_level)

    handler = logging.StreamHandler()
    handler.setFormatter(
        JsonLogFormatter(service=settings.app_name, environment=settings.app_env.value)
    )

    root.handlers.clear()
    root.addHandler(handler)
