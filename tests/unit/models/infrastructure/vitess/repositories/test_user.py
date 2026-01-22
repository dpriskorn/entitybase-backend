"""Unit tests for UserRepository."""

import pytest
from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.user import UserRepository
from models.rest_api.entitybase.v1.request.enums import UserActivityType


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
