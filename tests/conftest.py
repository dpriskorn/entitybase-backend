"""Shared pytest fixtures for all test types."""

import sys

import pytest

sys.path.insert(0, "src")


def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers", "requires_kafka: tests that require Kafka/Redpanda to be running"
    )


def pytest_collection_modifyitems(config, items):
    """Skip tests marked with requires_kafka when Kafka is not available."""
    skip_marker = pytest.mark.skip(reason="Kafka/Redpanda not available")
    for item in items:
        if "requires_kafka" in item.keywords:
            item.add_marker(skip_marker)


@pytest.fixture
def api_prefix():
    """Return the API prefix from settings.

    This fixture provides the API version prefix (e.g., "/v1/entitybase")
    to all tests, allowing the API version to be controlled from settings
    rather than being hardcoded throughout the test suite.
    """
    from models.config.settings import settings

    return settings.api_prefix
