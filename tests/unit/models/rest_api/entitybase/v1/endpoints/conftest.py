"""Fixtures for entitybase v1 endpoint tests."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_entity_read_state():
    """Create a properly mocked state for EntityReadHandler tests."""
    mock_state = MagicMock()
    mock_vitess = MagicMock()
    mock_s3 = MagicMock()

    mock_state.vitess_client = mock_vitess
    mock_state.s3_client = mock_s3

    mock_vitess.entity_exists.return_value = True
    mock_vitess.get_head.return_value = 12345

    yield mock_state, mock_vitess, mock_s3
