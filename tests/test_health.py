from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "bakunity-infra"}
    assert response.headers["X-Request-ID"]


def test_health_preserves_safe_request_id() -> None:
    response = client.get("/health", headers={"X-Request-ID": "req-test-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-test-123"


def test_health_replaces_unsafe_request_id() -> None:
    response = client.get("/health", headers={"X-Request-ID": "unsafe request id"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "unsafe request id"
    assert len(response.headers["X-Request-ID"]) == 32
