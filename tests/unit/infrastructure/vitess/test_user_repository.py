import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, "src")

from models.infrastructure.vitess.user_repository import UserRepository
from models.user import User


class TestUserRepository:
    """Unit tests for UserRepository"""

    @pytest.fixture
    def mock_connection_manager(self) -> MagicMock:
        """Mock connection manager"""
        return MagicMock()

    @pytest.fixture
    def repository(self, mock_connection_manager: MagicMock) -> UserRepository:
        """Create repository instance"""
        return UserRepository(mock_connection_manager)

    def test_create_user_new(
        self, repository: UserRepository, mock_connection_manager: MagicMock
    ) -> None:
        """Test creating a new user"""
        mock_conn = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        repository.create_user(12345)

        mock_cursor.execute.assert_called_once_with(
            """
            INSERT INTO users (user_id)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE user_id = user_id
            """,
            (12345,),
        )

    def test_user_exists_true(
        self, repository: UserRepository, mock_connection_manager: MagicMock
    ) -> None:
        """Test checking if user exists - returns True"""
        mock_conn = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (12345,)

        result = repository.user_exists(12345)

        assert result is True
        mock_cursor.execute.assert_called_once_with(
            "SELECT 1 FROM users WHERE user_id = %s",
            (12345,),
        )

    def test_user_exists_false(
        self, repository: UserRepository, mock_connection_manager: MagicMock
    ) -> None:
        """Test checking if user exists - returns False"""
        mock_conn = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = repository.user_exists(12345)

        assert result is False

    def test_get_user_found(
        self, repository: UserRepository, mock_connection_manager: MagicMock
    ) -> None:
        """Test getting user data when user exists"""
        from datetime import datetime

        mock_conn = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        mock_cursor.fetchone.return_value = (12345, created_at, {"theme": "dark"})

        result = repository.get_user(12345)

        assert result is not None
        assert isinstance(result, User)
        assert result.user_id == 12345
        assert result.created_at == created_at
        assert result.preferences == {"theme": "dark"}

    def test_get_user_not_found(
        self, repository: UserRepository, mock_connection_manager: MagicMock
    ) -> None:
        """Test getting user data when user doesn't exist"""
        mock_conn = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = repository.get_user(12345)

        assert result is None
