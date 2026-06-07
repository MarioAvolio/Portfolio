"""Shared test fixtures for the gateway.

Downstream base URLs are pointed at an unused localhost port so health probes
and proxy calls fail fast with a connection error — letting the suite exercise
the gateway's routing and degradation logic with no services running.

The client is used as a context manager so the application lifespan runs and the
shared HTTP client is created.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from backend.__main__ import get_app
from backend.webserver.configurations import get_configs


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Yields a TestClient whose registry points at a dead port."""
    monkeypatch.setenv("TEXT_INTELLIGENCE_URL", "http://127.0.0.1:0")
    monkeypatch.setenv("INSURELLM_URL", "http://127.0.0.1:0")
    monkeypatch.setenv("DEEP_RESEARCH_URL", "http://127.0.0.1:0")
    get_configs.cache_clear()
    with TestClient(get_app()) as test_client:
        yield test_client
