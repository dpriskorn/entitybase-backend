"""Unit tests for connection."""

from unittest.mock import MagicMock, patch

from models.infrastructure.vitess.connection import VitessConnectionManager
from models.data.config.vitess import VitessConfig


class TestVitessConnectionManager:
    """Unit tests for VitessConnectionManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = VitessConfig(
            host="localhost",
            port=3306,
            user="user",
            password="pass",
            database="test_db"
        )

        """Test healthy connection check success."""
        manager = VitessConnectionManager(config=self.config)
        mock_connection = MagicMock()
        manager.connection = mock_connection

        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)

        result = manager.healthy_connection

        assert result is True
        mock_cursor.execute.assert_called_once_with("SELECT 1")
        mock_cursor.close.assert_called_once()


        """Test healthy connection connects and performs check."""
        manager = VitessConnectionManager(config=self.config)
        manager.connection = None

        with patch('models.infrastructure.vitess.connection.pymysql.connect') as mock_connect:
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection
            mock_cursor = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (1,)

            result = manager.healthy_connection

            assert result is True
            mock_connect.assert_called_once()
            mock_cursor.execute.assert_called_once_with("SELECT 1")


        """Test disconnecting when connection exists."""
        manager = VitessConnectionManager(config=self.config)
        mock_connection = MagicMock()
        manager.connection = mock_connection

        manager.disconnect()

        mock_connection.close.assert_called_once()
        assert manager.connection is None


        """Test destructor calls disconnect."""
        manager = VitessConnectionManager(config=self.config)
        mock_connection = MagicMock()
        manager.connection = mock_connection

        with patch.object(manager, 'disconnect') as mock_disconnect:
            del manager
            mock_disconnect.assert_called_once()
