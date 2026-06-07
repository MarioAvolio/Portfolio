"""Shared test fixtures for the deep-research service."""

import pytest
from fastapi.testclient import TestClient

from deep_research.__main__ import get_app
from deep_research.webserver.configurations import get_configs
from deep_research.webserver.dependency.deps import _job_store_singleton


@pytest.fixture
def client() -> TestClient:
    """Returns a TestClient bound to a fresh app instance with a clean job store."""
    get_configs.cache_clear()
    _job_store_singleton.cache_clear()
    return TestClient(get_app())
