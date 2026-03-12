"""Unit tests for user preferences handler."""

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException


class TestUserPreferencesHandlerMethods:
    """Test UserPreferencesHandler methods with mocks."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        state.vitess_client = MagicMock()
        return state

    @pytest.fixture
    def handler(self, mock_state):
        """Create handler with mock state."""
        from models.rest_api.entitybase.v1.handlers.user_preferences import (
            UserPreferencesHandler,
        )

        handler = UserPreferencesHandler(state=mock_state)
        return handler

    def test_get_preferences_not_found(self, handler, mock_state):
        """Test get_preferences raises 404 when user not found."""
        mock_state.vitess_client.user_repository.user_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            handler.get_preferences(99999)

        assert exc_info.value.status_code == 404
