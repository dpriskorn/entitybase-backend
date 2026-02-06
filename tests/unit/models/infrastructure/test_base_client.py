"""Unit tests for Client base class."""

from unittest.mock import MagicMock

import pytest

from models.data.config.config import Config
from models.infrastructure.client import Client


class TestClient:
    """Unit tests for Client base class."""

    def test_healthy_connection_with_connection_manager(self) -> None:
        """Test healthy_connection returns True when connection_manager is healthy."""
        mock_config = MagicMock(spec=Config)
        mock_connection_manager = MagicMock()
        mock_connection_manager.healthy_connection = True

        client = Client(config=mock_config)
        client.connection_manager = mock_connection_manager

        assert client.healthy_connection is True

    def test_healthy_connection_false_when_unhealthy(self) -> None:
        """Test healthy_connection returns False when connection is unhealthy."""
        mock_config = MagicMock(spec=Config)
        mock_connection_manager = MagicMock()
        mock_connection_manager.healthy_connection = False

        client = Client(config=mock_config)
        client.connection_manager = mock_connection_manager

        assert client.healthy_connection is False

    def test_healthy_connection_without_connection_manager(self) -> None:
        """Test healthy_connection raises 503 error when connection_manager is None."""
        from fastapi import HTTPException

        mock_config = MagicMock(spec=Config)

        client = Client(config=mock_config)

        with pytest.raises((ValueError, HTTPException)):  # raise_validation_error raises ValueError or HTTPException
            _ = client.healthy_connection
