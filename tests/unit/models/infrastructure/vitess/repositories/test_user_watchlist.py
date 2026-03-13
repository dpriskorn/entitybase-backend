"""Unit tests for UserRepository - watchlist operations."""

import pytest
from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.user import UserRepository


class TestUserRepositoryWatchlist:
    """Unit tests for UserRepository watchlist operations."""

    def test_is_watchlist_enabled_true(self):
        """Test checking if watchlist is enabled."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = (True,)
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.is_watchlist_enabled(123)

        assert result is True

    def test_is_watchlist_enabled_false(self):
        """Test checking if watchlist is disabled."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = (False,)
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.is_watchlist_enabled(123)

        assert result is False

    def test_is_watchlist_enabled_no_user(self):
        """Test checking watchlist for non-existent user."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.is_watchlist_enabled(123)

        assert result is False

    def test_is_watchlist_enabled_user_not_found(self):
        """Test watchlist check for non-existent user."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.is_watchlist_enabled(123)

        assert result is False

    def test_is_watchlist_enabled_database_error(self):
        """Test watchlist check with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        with pytest.raises(Exception):
            repo.is_watchlist_enabled(123)

    def test_set_watchlist_enabled_success(self):
        """Test enabling watchlist."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
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

    def test_set_watchlist_enabled_database_error(self):
        """Test setting watchlist with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.set_watchlist_enabled(123, True)

        assert result.success is False
        assert "DB error" in result.error

    def test_enable_watchlist(self):
        """Test enabling watchlist."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.enable_watchlist(123)

        assert result.success is True
        mock_cursor.execute.assert_called_with(
            "UPDATE users SET watchlist_enabled = %s WHERE user_id = %s",
            (True, 123),
        )

    def test_disable_watchlist(self):
        """Test disabling watchlist."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_vitess_client.cursor = mock_cursor

        repo = UserRepository(vitess_client=mock_vitess_client)

        result = repo.disable_watchlist(123)

        assert result.success is True
        mock_cursor.execute.assert_called_with(
            "UPDATE users SET watchlist_enabled = %s WHERE user_id = %s",
            (False, 123),
        )
