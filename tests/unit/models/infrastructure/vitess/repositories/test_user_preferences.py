"""Unit tests for UserRepository - preferences operations."""

import pytest
from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.user import UserRepository


class TestUserRepositoryPreferences:
    """Unit tests for UserRepository preferences operations."""

    def test_get_user_preferences_success(self):
        """Test getting user preferences."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
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
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_preferences(123)

        assert result.success is False
        assert "User preferences not found" in result.error

    def test_get_user_preferences_invalid_id(self):
        """Test getting preferences with invalid ID."""
        mock_vitess_client = MagicMock()

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_preferences(0)

        assert result.success is False
        assert "Invalid user ID" in result.error

    def test_get_user_preferences_database_error(self):
        """Test getting preferences with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_preferences(123)

        assert result.success is False
        assert "DB error" in result.error

    def test_update_user_preferences_success(self):
        """Test updating user preferences."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
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

    def test_update_user_preferences_database_error(self):
        """Test updating preferences with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.update_user_preferences(100, 48, 123)

        assert result.success is False
        assert "DB error" in result.error
