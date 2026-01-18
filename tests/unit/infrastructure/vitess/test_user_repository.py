"""Unit tests for UserRepository."""

import pytest
from unittest.mock import MagicMock, Mock

from models.infrastructure.vitess.user_repository import UserRepository
from models.common import OperationResult
from models.user import User
from models.user_activity import ActivityType


class TestUserRepository:
    """Test cases for UserRepository."""

    @pytest.fixture
    def mock_connection_manager(self):
        """Mock connection manager."""
        return MagicMock()

    @pytest.fixture
    def repository(self, mock_connection_manager):
        """Create repository with mocked connection manager."""
        return UserRepository(mock_connection_manager)

    def test_create_user_success(self, repository, mock_connection_manager):
        """Test successful user creation."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = repository.create_user(123)

        assert result.success is True
        mock_cursor.execute.assert_called_once_with(
            "\n                        INSERT INTO users (user_id)\n                        VALUES (%s)\n                        ON DUPLICATE KEY UPDATE user_id = user_id\n                        ",
            (123,),
        )

    def test_create_user_database_error(self, repository, mock_connection_manager):
        """Test user creation with database error."""
        mock_connection_manager.get_connection.side_effect = Exception("DB error")

        result = repository.create_user(123)

        assert result.success is False
        assert "DB error" in result.error

    def test_user_exists_true(self, repository, mock_connection_manager):
        """Test user exists returns True."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)

        result = repository.user_exists(123)

        assert result is True
        mock_cursor.execute.assert_called_once_with(
            "SELECT 1 FROM users WHERE user_id = %s",
            (123,),
        )

    def test_user_exists_false(self, repository, mock_connection_manager):
        """Test user exists returns False."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = repository.user_exists(123)

        assert result is False

    def test_get_user_success(self, repository, mock_connection_manager):
        """Test successful user retrieval."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (123, "2023-01-01", {"key": "value"})

        result = repository.get_user(123)

        assert result is not None
        assert result.user_id == 123
        assert result.created_at == "2023-01-01"
        assert result.preferences == {"key": "value"}

    def test_get_user_not_found(self, repository, mock_connection_manager):
        """Test user retrieval when not found."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = repository.get_user(123)

        assert result is None

    def test_update_user_activity_success(self, repository, mock_connection_manager):
        """Test successful user activity update."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = repository.update_user_activity(123)

        assert result.success is True
        mock_cursor.execute.assert_called_once_with(
            "UPDATE users SET last_activity = NOW() WHERE user_id = %s",
            (123,),
        )

    def test_update_user_activity_invalid_user_id(self, repository):
        """Test update user activity with invalid user ID."""
        result = repository.update_user_activity(0)

        assert result.success is False
        assert "Invalid user ID" in result.error

    def test_update_user_activity_database_error(
        self, repository, mock_connection_manager
    ):
        """Test update user activity with database error."""
        mock_connection_manager.get_connection.side_effect = Exception("DB error")

        result = repository.update_user_activity(123)

        assert result.success is False
        assert "DB error" in result.error

    def test_is_watchlist_enabled_true(self, repository, mock_connection_manager):
        """Test watchlist enabled returns True."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)

        result = repository.is_watchlist_enabled(123)

        assert result is True

    def test_is_watchlist_enabled_false(self, repository, mock_connection_manager):
        """Test watchlist enabled returns False."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (0,)

        result = repository.is_watchlist_enabled(123)

        assert result is False

    def test_is_watchlist_enabled_no_user(self, repository, mock_connection_manager):
        """Test watchlist enabled when user not found."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = repository.is_watchlist_enabled(123)

        assert result is False

    def test_set_watchlist_enabled_success(self, repository, mock_connection_manager):
        """Test successful watchlist enable/disable."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = repository.set_watchlist_enabled(123, True)

        assert result.success is True
        mock_cursor.execute.assert_called_once_with(
            "UPDATE users SET watchlist_enabled = %s WHERE user_id = %s",
            (True, 123),
        )

    def test_set_watchlist_enabled_invalid_user_id(self, repository):
        """Test set watchlist with invalid user ID."""
        result = repository.set_watchlist_enabled(0, True)

        assert result.success is False
        assert "Invalid user ID" in result.error

    def test_disable_watchlist(self, repository, mock_connection_manager):
        """Test disable watchlist calls set_watchlist_enabled."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = repository.disable_watchlist(123)

        assert result.success is True
        mock_cursor.execute.assert_called_once_with(
            "UPDATE users SET watchlist_enabled = %s WHERE user_id = %s",
            (False, 123),
        )

    def test_log_user_activity_success(self, repository, mock_connection_manager):
        """Test successful user activity logging."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = repository.log_user_activity(123, ActivityType.EDIT, "Q42", 456)

        assert result.success is True
        mock_cursor.execute.assert_called_once_with(
            "\n                        INSERT INTO user_activity (user_id, activity_type, entity_id, revision_id)\n                        VALUES (%s, %s, %s, %s)\n                        ",
            (123, "edit", "Q42", 456),
        )

    def test_log_user_activity_invalid_user_id(self, repository):
        """Test log user activity with invalid user ID."""
        result = repository.log_user_activity(0, ActivityType.EDIT, "Q42")

        assert result.success is False
        assert "Invalid user ID" in result.error

    def test_log_user_activity_invalid_activity_type(self, repository):
        """Test log user activity with invalid activity type."""
        result = repository.log_user_activity(123, None, "Q42")

        assert result.success is False
        assert "Invalid user ID or activity type" in result.error

    def test_get_user_preferences_success(self, repository, mock_connection_manager):
        """Test successful user preferences retrieval."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (10, 24)

        result = repository.get_user_preferences(123)

        assert result.success is True
        assert result.data == {"notification_limit": 10, "retention_hours": 24}

    def test_get_user_preferences_invalid_user_id(self, repository):
        """Test get user preferences with invalid user ID."""
        result = repository.get_user_preferences(0)

        assert result.success is False
        assert "Invalid user ID" in result.error

    def test_get_user_preferences_not_found(self, repository, mock_connection_manager):
        """Test get user preferences when user not found."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = repository.get_user_preferences(123)

        assert result.success is False
        assert "User preferences not found" in result.error

    def test_update_user_preferences_success(self, repository, mock_connection_manager):
        """Test successful user preferences update."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = repository.update_user_preferences(10, 24, 123)

        assert result.success is True
        mock_cursor.execute.assert_called_once_with(
            "UPDATE users SET notification_limit = %s, retention_hours = %s WHERE user_id = %s",
            (10, 24, 123),
        )

    def test_update_user_preferences_invalid_user_id(self, repository):
        """Test update user preferences with invalid user ID."""
        result = repository.update_user_preferences(10, 24, 0)

        assert result.success is False
        assert "Invalid user ID" in result.error

    def test_get_user_activities_success(self, repository, mock_connection_manager):
        """Test successful user activities retrieval."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 123, "edit", "Q42", 456, "2023-01-01"),
        ]

        result = repository.get_user_activities(123)

        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0].user_id == 123

    def test_get_user_activities_with_filters(
        self, repository, mock_connection_manager
    ):
        """Test user activities with activity type filter."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        result = repository.get_user_activities(123, ActivityType.EDIT, 48, 100, 10)

        assert result.success is True
        # Check query includes activity_type filter
        call_args = mock_cursor.execute.call_args
        query = call_args[0][0]
        assert "AND activity_type = %s" in query

    def test_get_user_activities_invalid_params(self, repository):
        """Test get user activities with invalid parameters."""
        result = repository.get_user_activities(0)
        assert result.success is False
        assert "user_id must be positive" in result.error

        result = repository.get_user_activities(123, hours=0)
        assert result.success is False
        assert "hours must be positive" in result.error

        result = repository.get_user_activities(123, limit=0)
        assert result.success is False
        assert "limit must be positive" in result.error

        result = repository.get_user_activities(123, offset=-1)
        assert result.success is False
        assert "offset must be non-negative" in result.error
