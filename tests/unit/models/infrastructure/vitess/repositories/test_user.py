"""Unit tests for UserRepository."""

import pytest
from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.user import UserRepository
from models.data.rest_api.v1.entitybase.request import UserActivityType


class TestUserRepository:
    """Unit tests for UserRepository."""

    def test_create_user_success(self):
        """Test successful user creation."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.create_user(123)

        assert result.success is True
        mock_cursor.execute.assert_called_once()

    def test_create_user_database_error(self):
        """Test user creation with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.create_user(123)

        assert result.success is False
        assert "DB error" in result.error

    def test_user_exists_true(self):
        """Test user exists when found."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.user_exists(123)

        assert result is True
        mock_cursor.execute.assert_called_once_with(
            "SELECT 1 FROM users WHERE user_id = %s", (123,)
        )

    def test_user_exists_false(self):
        """Test user does not exist."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.user_exists(123)

        assert result is False

    def test_get_user_found(self):
        """Test getting existing user."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (123, "2023-01-01", {"theme": "dark"})
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.get_user(123)

        assert result is not None
        assert result.user_id == 123
        assert result.preferences == {"theme": "dark"}

    def test_get_user_not_found(self):
        """Test getting non-existent user."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.get_user(123)

        assert result is None

    def test_update_user_activity_success(self):
        """Test successful user activity update."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.update_user_activity(123)

        assert result.success is True

    def test_update_user_activity_invalid_id(self):
        """Test user activity update with invalid ID."""
        mock_vitess_client = MagicMock()

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.update_user_activity(0)

        assert result.success is False
        assert "Invalid user ID" in result.error

    def test_is_watchlist_enabled_true(self):
        """Test checking if watchlist is enabled."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (True,)
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.is_watchlist_enabled(123)

        assert result is True

    def test_is_watchlist_enabled_false(self):
        """Test checking if watchlist is disabled."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (False,)
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.is_watchlist_enabled(123)

        assert result is False

    def test_is_watchlist_enabled_no_user(self):
        """Test checking watchlist for non-existent user."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.is_watchlist_enabled(123)

        assert result is False

    def test_set_watchlist_enabled_success(self):
        """Test enabling watchlist."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.set_watchlist_enabled(123, True)

        assert result.success is True

    def test_set_watchlist_enabled_invalid_id(self):
        """Test setting watchlist with invalid ID."""
        mock_vitess_client = MagicMock()

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.set_watchlist_enabled(0, True)

        assert result.success is False
        assert "Invalid user ID" in result.error

    def test_disable_watchlist(self):
        """Test disabling watchlist."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.disable_watchlist(123)

        assert result.success is True
        mock_cursor.execute.assert_called_with(
            "UPDATE users SET watchlist_enabled = %s WHERE user_id = %s",
            (False, 123),
        )

    def test_log_user_activity_success(self):
        """Test logging user activity."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        from models.data.rest_api.v1.entitybase.request import UserActivityType
        result = repo.log_user_activity(123, UserActivityType.ENTITY_EDIT, "Q1", 1)

        assert result.success is True



    def test_get_user_preferences_success(self):
        """Test getting user preferences."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (50, 24)
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_preferences(123)

        assert result.success is True
        assert result.data["notification_limit"] == 50
        assert result.data["retention_hours"] == 24

    def test_get_user_preferences_not_found(self):
        """Test getting preferences for non-existent user."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_preferences(123)

        assert result.success is False
        assert "User preferences not found" in result.error

    def test_update_user_preferences_success(self):
        """Test updating user preferences."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.update_user_preferences(100, 48, 123)

        assert result.success is True

    def test_update_user_preferences_invalid_id(self):
        """Test updating preferences with invalid ID."""
        mock_vitess_client = MagicMock()

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.update_user_preferences(100, 48, 0)

        assert result.success is False
        assert "Invalid user ID" in result.error



    def test_get_user_activities_invalid_params(self):
        """Test getting activities with invalid params."""
        mock_vitess_client = MagicMock()

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_activities(0)

        assert result.success is False
        assert "user_id must be positive" in result.error

    def test_create_user_success_new(self):
        """Test successful user creation for new user."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # user doesn't exist
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.create_user(123)

        assert result.success is True



    def test_get_user_not_found_case(self):
        """Test getting non-existent user."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.get_user(123)

        assert result is None

    def test_update_user_activity_database_error(self):
        """Test user activity update with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.update_user_activity(123)

        assert result.success is False
        assert "DB error" in result.error

    def test_is_watchlist_enabled_user_not_found(self):
        """Test watchlist check for non-existent user."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.is_watchlist_enabled(123)

        assert result is False

    def test_set_watchlist_enabled_database_error(self):
        """Test setting watchlist with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.set_watchlist_enabled(123, True)

        assert result.success is False
        assert "DB error" in result.error

    def test_get_user_preferences_user_not_found(self):
        """Test getting preferences for non-existent user."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_preferences(123)

        assert result.success is False
        assert "User preferences not found" in result.error

    def test_update_user_preferences_database_error(self):
        """Test updating preferences with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.update_user_preferences(100, 48, 123)

        assert result.success is False
        assert "DB error" in result.error

    def test_get_user_activities_no_activities(self):
        """Test getting activities when user has none."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []  # no activities
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_activities(123)

        assert result.success is True
        assert result.data == []

    def test_user_exists_database_error(self):
        """Test user exists with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        with pytest.raises(Exception):  # since it doesn't catch
            repo.user_exists(123)

    def test_get_user_database_error(self):
        """Test get user with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        with pytest.raises(Exception):
            repo.get_user(123)

    def test_is_watchlist_enabled_database_error(self):
        """Test watchlist check with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        with pytest.raises(Exception):
            repo.is_watchlist_enabled(123)

    def test_log_user_activity_database_error(self):
        """Test logging activity with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.log_user_activity(123, UserActivityType.ENTITY_EDIT, "Q1", 1)

        assert result.success is False
        assert "DB error" in result.error
