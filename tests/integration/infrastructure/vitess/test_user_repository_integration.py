import sys
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, "src")

from models.infrastructure.vitess.repositories.user import UserRepository
from models.user import User
from models.rest_api.entitybase.request.enums import UserActivityType


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

    def test_update_user_activity(
        self, repository: UserRepository, mock_connection_manager: MagicMock
    ) -> None:
        """Test updating user activity"""
        mock_conn = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        repository.update_user_activity(12345)

        mock_cursor.execute.assert_called_once_with(
            "UPDATE users SET last_activity = NOW() WHERE user_id = %s",
            (12345,),
        )

    def test_is_watchlist_enabled(
        self, repository: UserRepository, mock_connection_manager: MagicMock
    ) -> None:
        """Test checking if watchlist is enabled"""
        mock_conn = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (True,)

        result = repository.is_watchlist_enabled(12345)

        assert result is True
        mock_cursor.execute.assert_called_once_with(
            "SELECT watchlist_enabled FROM users WHERE user_id = %s",
            (12345,),
        )

    def test_set_watchlist_enabled(
        self, repository: UserRepository, mock_connection_manager: MagicMock
    ) -> None:
        """Test setting watchlist enabled status"""
        mock_conn = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        repository.set_watchlist_enabled(12345, False)

        mock_cursor.execute.assert_called_once_with(
            "UPDATE users SET watchlist_enabled = %s WHERE user_id = %s",
            (False, 12345),
        )

    def test_disable_watchlist(
        self, repository: UserRepository, mock_connection_manager: MagicMock
    ) -> None:
        """Test disabling watchlist"""
        mock_conn = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        repository.disable_watchlist(12345)

        mock_cursor.execute.assert_called_once_with(
            "UPDATE users SET watchlist_enabled = %s WHERE user_id = %s",
            (False, 12345),
        )

    def test_get_user_preferences(
        self, repository: UserRepository, mock_connection_manager: MagicMock
    ) -> None:
        """Test getting user preferences"""
        mock_conn = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (100, 72)

        result = repository.get_user_preferences(12345)

        assert result == {"notification_limit": 100, "retention_hours": 72}
        mock_cursor.execute.assert_called_once_with(
            "SELECT notification_limit, retention_hours FROM users WHERE user_id = %s",
            (12345,),
        )

    def test_update_user_preferences(
        self, repository: UserRepository, mock_connection_manager: MagicMock
    ) -> None:
        """Test updating user preferences"""
        mock_conn = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        repository.update_user_preferences(12345, 200, 168)

        mock_cursor.execute.assert_called_once_with(
            "UPDATE users SET notification_limit = %s, retention_hours = %s WHERE user_id = %s",
            (200, 168, 12345),
        )

    def test_log_user_activity(
        self, repository: UserRepository, mock_connection_manager: MagicMock
    ) -> None:
        """Test logging user activity"""
        mock_conn = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        repository.log_user_activity(12345, UserActivityType.EDIT, "Q42", 123)

        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO user_activity (user_id, activity_type, entity_id, revision_id) VALUES (%s, %s, %s, %s)",
            (12345, "edit", "Q42", 123),
        )

    def test_get_user_activities(
        self, repository: UserRepository, mock_connection_manager: MagicMock
    ) -> None:
        """Test getting user activities"""
        from models.rest_api.entitybase.response.user_activity import UserActivityItemResponse

        mock_conn = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 12345, "entity_revert", "Q42", 123, "2023-01-01T12:00:00"),
            (2, 12345, "entity_edit", "Q43", 124, "2023-01-02T12:00:00"),
        ]

        result = repository.get_user_activities(12345, limit=30, offset=0)

        assert len(result) == 2
        assert isinstance(result[0], UserActivityItemResponse)
        assert result[0].id == 1
        assert result[0].user_id == 12345
        assert result[0].activity_type == "entity_revert"
        assert result[0].entity_id == "Q42"
        assert result[0].revision_id == 123
