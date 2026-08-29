from __future__ import annotations

import logging
from time import perf_counter

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from infrastructure.observability import normalize_request_id, reset_request_id, set_request_id

logger = logging.getLogger(__name__)


class RequestContextMiddleware:
    """Bind a safe request id to the current async context and response."""

    def __init__(self, app: ASGIApp, *, header_name: str = "X-Request-ID") -> None:
        self.app = app
        self.header_name = header_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        incoming = Headers(scope=scope).get(self.header_name)
        request_id = normalize_request_id(incoming)
        token = set_request_id(request_id)
        started = perf_counter()
        status_code = 500

        async def send_with_request_id(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                MutableHeaders(scope=message)[self.header_name] = request_id
            await send(message)

        log_extra = {
            "event": "http_request",
            "method": scope.get("method", ""),
            "path": scope.get("path", ""),
        }

        try:
            await self.app(scope, receive, send_with_request_id)
        except Exception:
            logger.exception(
                "http_request_failed",
                extra={
                    **log_extra,
                    "status_code": 500,
                    "duration_ms": round((perf_counter() - started) * 1000, 3),
                },
            )
            raise
        else:
            logger.info(
                "http_request_completed",
                extra={
                    **log_extra,
                    "status_code": status_code,
                    "duration_ms": round((perf_counter() - started) * 1000, 3),
                },
            )
        finally:
            reset_request_id(token)
