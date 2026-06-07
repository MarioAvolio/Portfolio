"""Shared test fixtures for the deep-research service."""

import pytest
from fastapi.testclient import TestClient

from deep_research.__main__ import get_app
from deep_research.webserver.configurations import get_configs


@pytest.fixture
def client() -> TestClient:
    """Returns a TestClient bound to a fresh app instance."""
    get_configs.cache_clear()
    return TestClient(get_app())
