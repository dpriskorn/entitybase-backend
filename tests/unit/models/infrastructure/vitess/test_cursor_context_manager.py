"""Unit tests for CursorContextManager."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from models.infrastructure.vitess.connection import CursorContextManager


class TestCursorContextManager:
    """Tests for CursorContextManager class."""

    def test_enter_acquires_connection_and_creates_cursor(self):
        """Test that __enter__ acquires connection and creates cursor."""
        mock_connection_manager = Mock()
        mock_connection = Mock()
        mock_connection.open = True
        mock_connection_manager.acquire.return_value = mock_connection
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        context_manager = CursorContextManager(mock_connection_manager)

        with context_manager as cursor:
            assert cursor is mock_cursor
            mock_connection_manager.acquire.assert_called_once()
            mock_connection.cursor.assert_called_once()

    def test_exit_closes_cursor_and_releases_connection(self):
        """Test that __exit__ closes cursor and releases connection."""
        mock_connection_manager = Mock()
        mock_connection = Mock()
        mock_connection.open = True
        mock_connection_manager.acquire.return_value = mock_connection
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        context_manager = CursorContextManager(mock_connection_manager)

        with context_manager:
            pass

        mock_cursor.close.assert_called_once()
        mock_connection_manager.release.assert_called_once_with(mock_connection)

    def test_exit_with_exception_still_releases_connection(self):
        """Test that connection is released even when exception occurs."""
        mock_connection_manager = Mock()
        mock_connection = Mock()
        mock_connection.open = True
        mock_connection_manager.acquire.return_value = mock_connection
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        context_manager = CursorContextManager(mock_connection_manager)

        with pytest.raises(ValueError):
            with context_manager:
                raise ValueError("Test error")

        mock_cursor.close.assert_called_once()
        mock_connection_manager.release.assert_called_once_with(mock_connection)

    def test_exit_with_closed_connection_does_not_release(self):
        """Test that closed connections are not released back to pool."""
        mock_connection_manager = Mock()
        mock_connection = Mock()
        mock_connection.open = False
        mock_connection_manager.acquire.return_value = mock_connection
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        context_manager = CursorContextManager(mock_connection_manager)

        with context_manager:
            pass

        mock_cursor.close.assert_called_once()
        mock_connection_manager.release.assert_not_called()

    def test_exit_with_none_connection_raises_error(self):
        """Test that None connection raises RuntimeError in __enter__."""
        mock_connection_manager = Mock()
        mock_connection_manager.acquire.return_value = None

        context_manager = CursorContextManager(mock_connection_manager)

        with pytest.raises(
            RuntimeError, match="Failed to acquire connection from pool"
        ):
            with context_manager:
                pass

        mock_connection_manager.release.assert_not_called()

    def test_cursor_close_exception_logged_and_continues(self):
        """Test that cursor close exception is logged and connection still released."""
        mock_connection_manager = Mock()
        mock_connection = Mock()
        mock_connection.open = True
        mock_connection_manager.acquire.return_value = mock_connection
        mock_cursor = Mock()
        mock_cursor.close.side_effect = Exception("Cursor close error")
        mock_connection.cursor.return_value = mock_cursor

        context_manager = CursorContextManager(mock_connection_manager)

        with context_manager:
            pass

        mock_cursor.close.assert_called_once()
        mock_connection_manager.release.assert_called_once_with(mock_connection)

    def test_connection_release_exception_logged(self):
        """Test that connection release exception is logged."""
        mock_connection_manager = Mock()
        mock_connection = Mock()
        mock_connection.open = True
        mock_connection_manager.acquire.return_value = mock_connection
        mock_connection_manager.release.side_effect = Exception("Release error")
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        context_manager = CursorContextManager(mock_connection_manager)

        with context_manager:
            pass

        mock_cursor.close.assert_called_once()
        mock_connection_manager.release.assert_called_once_with(mock_connection)
