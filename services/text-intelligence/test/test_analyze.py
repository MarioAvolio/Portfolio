"""Tests for the core ``/analyze`` endpoint (mock provider)."""

from fastapi.testclient import TestClient

PREFIX = "/text-intelligence/api/v1"


def test_analyze_returns_structured_result(client: TestClient) -> None:
    response = client.post(
        f"{PREFIX}/analyze",
        json={"text": "I love this great product. It works really well."},
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"summary", "sentiment", "tags", "language", "model"}
    assert body["sentiment"] == "positive"
    assert body["model"] == "mock-1"
    assert isinstance(body["tags"], list)


def test_analyze_rejects_empty_text(client: TestClient) -> None:
    response = client.post(f"{PREFIX}/analyze", json={"text": ""})
    # Pydantic min_length=1 rejects at the validation layer.
    assert response.status_code == 422


def test_analyze_detects_italian(client: TestClient) -> None:
    response = client.post(
        f"{PREFIX}/analyze",
        json={"text": "Questo è un ottimo prodotto che funziona molto bene per tutti."},
    )
    assert response.status_code == 200
    assert response.json()["language"] == "it"
