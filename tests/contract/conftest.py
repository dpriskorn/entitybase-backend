"""Pytest configuration for contract tests."""

import sys
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, "src")


@pytest.fixture(autouse=True)
def initialized_app():
    """Initialize app with mocked StateHandler for contract tests.

    This fixture ensures app.state.state_handler is set before tests run,
    preventing 503 errors from StartupMiddleware. Uses mocks to avoid
    requiring external services (Vitess, S3).
    """
    from models.rest_api.main import app

    mock_state_handler = MagicMock()
    mock_state_handler.vitess_client = None
    mock_state_handler.s3_client = None
    mock_state_handler.enumeration_service = MagicMock()
    mock_state_handler.validator = MagicMock()
    mock_state_handler.disconnect = MagicMock()

    app.state.state_handler = mock_state_handler

    yield

    if hasattr(app.state, "state_handler"):
        delattr(app.state, "state_handler")


@pytest.fixture
def api_prefix():
    """Return the API prefix from settings."""
    from models.config.settings import settings

    return settings.api_prefix
