import json
import logging

from infrastructure.observability import JsonLogFormatter, reset_request_id, set_request_id


def test_json_log_formatter_adds_request_context() -> None:
    formatter = JsonLogFormatter(service="Bakunity Infra", environment="test")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="hello",
        args=(),
        exc_info=None,
    )
    record.event = "test_event"

    token = set_request_id("req-test-123")
    try:
        payload = json.loads(formatter.format(record))
    finally:
        reset_request_id(token)

    assert payload["message"] == "hello"
    assert payload["request_id"] == "req-test-123"
    assert payload["event"] == "test_event"
    assert payload["environment"] == "test"
