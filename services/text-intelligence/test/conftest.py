"""Shared test fixtures."""

import pytest
from fastapi.testclient import TestClient

from text_intelligence.__main__ import get_app
from text_intelligence.webserver.configurations import get_configs


@pytest.fixture
def client() -> TestClient:
    """Returns a TestClient bound to a fresh app instance.

    The configuration cache is cleared so each test sees defaults (mock
    provider) regardless of the host environment.
    """
    get_configs.cache_clear()
    return TestClient(get_app())
