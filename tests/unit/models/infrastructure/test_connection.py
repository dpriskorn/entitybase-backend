"""Unit tests for ConnectionManager base class."""

import pytest
from unittest.mock import MagicMock

from models.infrastructure.connection import ConnectionManager
from models.data.config.config import Config


class TestConnectionManager:
    """Unit tests for ConnectionManager base class."""

    def test_connect_method_exists(self) -> None:
        """Test that connect method exists and can be called."""
        mock_config = MagicMock(spec=Config)

        connection_manager = ConnectionManager(config=mock_config)

        result = connection_manager.connect()
        assert result is None

    def test_healthy_connection_not_implemented(self) -> None:
        """Test that healthy_connection property raises NotImplementedError."""
        mock_config = MagicMock(spec=Config)

        connection_manager = ConnectionManager(config=mock_config)

        with pytest.raises(NotImplementedError):
            _ = connection_manager.healthy_connection
