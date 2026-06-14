"""Shared test fixtures for market-sentinel tests."""

import pytest
from fastapi.testclient import TestClient

from market_sentinel.__main__ import get_app
from market_sentinel.webserver.configurations import get_configs
from market_sentinel.webserver.dependency.deps import _job_store_singleton, _report_store_singleton


@pytest.fixture
def client() -> TestClient:
    """Returns a TestClient bound to a fresh app instance with clean stores."""
    get_configs.cache_clear()
    _job_store_singleton.cache_clear()
    _report_store_singleton.cache_clear()
    return TestClient(get_app())
