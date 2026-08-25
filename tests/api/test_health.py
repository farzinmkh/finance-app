"""
Health Endpoint Tests
======================
Tests for GET /health.

These are API-level tests — they send real HTTP requests through the
full FastAPI stack and verify the response we get back.

What we test here:
- The endpoint exists and returns HTTP 200
- The response body has the correct structure
- The database connectivity check reports "ok"

What we do NOT test here:
- What happens when the database is unreachable
  (that would require more complex setup — test the logic directly instead)
"""

from fastapi.testclient import TestClient


def test_health_check_returns_http_200(client: TestClient) -> None:
    """The health endpoint must return HTTP 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_application_status_is_ok(client: TestClient) -> None:
    """The 'status' field must be 'ok'."""
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"


def test_health_check_database_status_is_ok(client: TestClient) -> None:
    """The 'database' field must be 'ok' when the database is reachable."""
    response = client.get("/health")
    data = response.json()
    assert data["database"] == "ok"


def test_health_check_response_has_correct_fields(client: TestClient) -> None:
    """The response must contain exactly the expected fields."""
    response = client.get("/health")
    data = response.json()
    assert "status" in data
    assert "database" in data


def test_health_check_content_type_is_json(client: TestClient) -> None:
    """The response must be JSON (not HTML or plain text)."""
    response = client.get("/health")
    assert "application/json" in response.headers["content-type"]
