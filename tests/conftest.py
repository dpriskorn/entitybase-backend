"""Shared pytest fixtures for all test types."""

import sys

import pytest

sys.path.insert(0, "src")


@pytest.fixture
def api_prefix():
    """Return the API prefix from settings.

    This fixture provides the API version prefix (e.g., "/v1/entitybase")
    to all tests, allowing the API version to be controlled from settings
    rather than being hardcoded throughout the test suite.
    """
    from models.config.settings import settings

    return settings.api_prefix
