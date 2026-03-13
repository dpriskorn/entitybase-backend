"""Unit tests for UserRepository - activity operations."""

import pytest
from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.user import UserRepository
from models.data.rest_api.v1.entitybase.request import UserActivityType


class TestUserRepositoryActivity:
    """Unit tests for UserRepository activity operations."""

    def test_update_user_activity_success(self):
        """Test successful user activity update."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
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

    def test_update_user_activity_database_error(self):
        """Test user activity update with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.update_user_activity(123)

        assert result.success is False
        assert "DB error" in result.error

    def test_log_user_activity_success(self):
        """Test logging user activity."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.log_user_activity(123, UserActivityType.ENTITY_EDIT, "Q1", 1)

        assert result.success is True

    def test_log_user_activity_invalid_user_id(self):
        """Test logging activity with invalid user ID."""
        mock_vitess_client = MagicMock()

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.log_user_activity(0, UserActivityType.ENTITY_EDIT, "Q1", 1)

        assert result.success is False
        assert "Invalid user ID or activity type" in result.error

    def test_log_user_activity_database_error(self):
        """Test logging activity with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.log_user_activity(123, UserActivityType.ENTITY_EDIT, "Q1", 1)

        assert result.success is False
        assert "DB error" in result.error

    def test_get_user_activities_invalid_params(self):
        """Test getting activities with invalid params."""
        mock_vitess_client = MagicMock()

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_activities(0)

        assert result.success is False
        assert "user_id must be positive" in result.error

    def test_get_user_activities_no_activities(self):
        """Test getting activities when user has none."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.return_value = []
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_activities(123)

        assert result.success is True
        assert result.data == []

    def test_get_user_activities_hours_invalid(self):
        """Test getting activities with invalid hours."""
        mock_vitess_client = MagicMock()

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_activities(123, hours=0)

        assert result.success is False
        assert "hours must be positive" in result.error

    def test_get_user_activities_limit_invalid(self):
        """Test getting activities with invalid limit."""
        mock_vitess_client = MagicMock()

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_activities(123, limit=0)

        assert result.success is False
        assert "limit must be positive" in result.error

    def test_get_user_activities_offset_invalid(self):
        """Test getting activities with invalid offset."""
        mock_vitess_client = MagicMock()

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_activities(123, offset=-1)

        assert result.success is False
        assert "offset must be non-negative" in result.error

    def test_get_user_activities_database_error(self):
        """Test getting activities with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.get_user_activities(123)

        assert result.success is False
        assert "DB error" in result.error
