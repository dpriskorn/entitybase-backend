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

    def test_initialization(self):
        """Test connection manager initialization."""
        with patch('models.infrastructure.vitess.connection.pymysql.connect') as mock_connect:
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection

            manager = VitessConnectionManager(config=self.config)

            assert manager.config == self.config
            assert manager.connection == mock_connection
            mock_connect.assert_called_once_with(
                host="localhost",
                port=3306,
                user="user",
                passwd="pass",
                database="test_db",
                autocommit=True,
            )

    def test_connect_when_none(self):
        """Test connecting when connection is None."""
        manager = VitessConnectionManager(config=self.config)
        manager.connection = None

        with patch('models.infrastructure.vitess.connection.pymysql.connect') as mock_connect:
            mock_connection = MagicMock()
            mock_connect.return_value = mock_connection

            manager.connect()

            assert manager.connection == mock_connection

    def test_connect_when_already_connected(self):
        """Test connecting when already connected."""
        manager = VitessConnectionManager(config=self.config)
        existing_connection = MagicMock()
        manager.connection = existing_connection

        manager.connect()

        # Should not create new connection
        assert manager.connection == existing_connection

    def test_healthy_connection_success(self):
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

    def test_healthy_connection_none_connects(self):
        """Test healthy connection when connection is None."""
        manager = VitessConnectionManager(config=self.config)
        manager.connection = None

        with patch.object(manager, 'connect') as mock_connect, \
             patch.object(manager, 'healthy_connection', new_callable=lambda: property(lambda self: True)):
            result = manager.healthy_connection

            mock_connect.assert_called_once()

    def test_healthy_connection_connects_and_checks(self):
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

    def test_healthy_connection_failure(self):
        """Test healthy connection check failure."""
        manager = VitessConnectionManager(config=self.config)
        mock_connection = MagicMock()
        manager.connection = mock_connection

        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Connection error")

        result = manager.healthy_connection

        assert result is False

    def test_disconnect_with_connection(self):
        """Test disconnecting when connection exists."""
        manager = VitessConnectionManager(config=self.config)
        mock_connection = MagicMock()
        manager.connection = mock_connection

        manager.disconnect()

        mock_connection.close.assert_called_once()
        assert manager.connection is None

    def test_disconnect_without_connection(self):
        """Test disconnecting when no connection exists."""
        manager = VitessConnectionManager(config=self.config)
        manager.connection = None

        manager.disconnect()

        # Should not raise error
        assert manager.connection is None

    def test_del_calls_disconnect(self):
        """Test destructor calls disconnect."""
        manager = VitessConnectionManager(config=self.config)
        mock_connection = MagicMock()
        manager.connection = mock_connection

        with patch.object(manager, 'disconnect') as mock_disconnect:
            del manager
            mock_disconnect.assert_called_once()
