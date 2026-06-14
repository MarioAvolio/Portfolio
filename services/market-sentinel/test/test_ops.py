"""Operational endpoint tests."""

from fastapi.testclient import TestClient


def test_openapi_schema_available(client: TestClient) -> None:
    """GET /openapi.json returns a valid OpenAPI schema."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()


def test_docs_returns_200(client: TestClient) -> None:
    """GET /docs returns 200 (Swagger UI)."""
    response = client.get("/docs")
    assert response.status_code == 200
