"""Shared test fixtures for the portfolio-assistant service."""

import pytest
from fastapi.testclient import TestClient

from portfolio_assistant.__main__ import get_app
from portfolio_assistant.webserver.configurations import get_configs


@pytest.fixture
def client() -> TestClient:
    """Returns a TestClient bound to a fresh app instance."""
    get_configs.cache_clear()
    return TestClient(get_app())
