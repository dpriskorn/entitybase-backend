"""Unit tests for user handler methods."""

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException


class TestUserHandlerMethods:
    """Test UserHandler methods with mocks."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        state.vitess_client = MagicMock()
        return state

    @pytest.fixture
    def handler(self, mock_state):
        """Create handler with mock state."""
        from models.rest_api.entitybase.v1.handlers.user import UserHandler

        handler = UserHandler(state=mock_state)
        return handler

    def test_toggle_watchlist_enable(self, handler, mock_state):
        """Test toggle_watchlist enables watchlist."""
        from models.data.rest_api.v1.entitybase.request import WatchlistToggleRequest

        mock_request = WatchlistToggleRequest(enabled=True)
        mock_state.vitess_client.user_repository.set_watchlist_enabled.return_value = (
            True
        )

        result = handler.toggle_watchlist(12345, mock_request)

        assert result is not None
        assert result.enabled is True

    def test_toggle_watchlist_disable(self, handler, mock_state):
        """Test toggle_watchlist disables watchlist."""
        from models.data.rest_api.v1.entitybase.request import WatchlistToggleRequest

        mock_request = WatchlistToggleRequest(enabled=False)
        mock_state.vitess_client.user_repository.set_watchlist_enabled.return_value = (
            True
        )

        result = handler.toggle_watchlist(12345, mock_request)

        assert result is not None
        assert result.enabled is False
