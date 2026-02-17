"""Pytest configuration for contract tests.

Contract tests validate API response schemas without requiring external services.
They use mock clients to simulate the Vitess and S3 backends.
"""

import logging
import sys

import pytest

sys.path.insert(0, "src")

from models.config.settings import settings

aws_loggers = [
    "botocore",
    "boto3",
    "urllib3",
    "s3transfer",
    "botocore.hooks",
    "botocore.retryhandler",
    "botocore.utils",
    "botocore.parsers",
    "botocore.endpoint",
    "botocore.auth",
]

for logger_name in aws_loggers:
    logging.getLogger(logger_name).setLevel(logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def initialized_app():
    """Initialize the FastAPI app with mock state_handler for contract tests.

    This fixture ensures app.state.state_handler is set to a TestStateHandler
    before tests run, preventing 503 errors from StartupMiddleware.
    Uses mocks to avoid requiring external services (Vitess, S3).
    """
    from models.rest_api.main import app
    from tests.contract.mocks import create_test_state_handler

    logger.debug("Creating TestStateHandler...")
    state_handler = create_test_state_handler()
    logger.debug("TestStateHandler created")

    app.state.state_handler = state_handler
    logger.debug(
        f"app.state.state_handler set: {type(app.state.state_handler).__name__}"
    )

    yield

    logger.debug("Disconnecting TestStateHandler...")
    if state_handler:
        state_handler.disconnect()
        logger.debug("TestStateHandler disconnected")
    if hasattr(app.state, "state_handler"):
        delattr(app.state, "state_handler")


@pytest.fixture
def api_prefix():
    """Return the API prefix from settings."""
    return settings.api_prefix
