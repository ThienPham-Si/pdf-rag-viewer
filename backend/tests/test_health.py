"""Tests for the GET /health endpoint.

Seam: Backend API boundary (integration tests).
Verifies the health check reports connection status for Postgres and Redis.
"""


async def test_health_returns_200(client):
    """GET /health always returns 200, even if backing services are down."""
    response = await client.get("/health")
    assert response.status_code == 200


async def test_health_response_has_required_keys(client):
    """Response body includes status, postgres, and redis fields."""
    response = await client.get("/health")
    body = response.json()
    assert "status" in body
    assert "postgres" in body
    assert "redis" in body


async def test_health_reports_service_status(client):
    """Each service reports either 'connected' or 'disconnected'."""
    response = await client.get("/health")
    body = response.json()
    assert body["postgres"] in ("connected", "disconnected")
    assert body["redis"] in ("connected", "disconnected")
    assert body["status"] in ("healthy", "degraded")
