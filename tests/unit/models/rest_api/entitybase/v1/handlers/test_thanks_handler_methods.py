"""Unit tests for thanks handler methods."""

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException


class TestThanksHandlerMethods:
    """Test ThanksHandler methods with mocks."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        state.vitess_client = MagicMock()
        return state

    @pytest.fixture
    def handler(self, mock_state):
        """Create handler with mock state."""
        from models.rest_api.entitybase.v1.handlers.thanks import ThanksHandler

        handler = ThanksHandler(state=mock_state)
        return handler

    def test_get_thanks_received_not_found(self, handler, mock_state):
        """Test get_thanks_received raises 404 when user not found."""
        from models.data.rest_api.v1.entitybase.request import ThanksListRequest

        mock_state.vitess_client.user_repository.user_exists.return_value = False
        mock_request = ThanksListRequest(hours=24, limit=50, offset=0)

        with pytest.raises(HTTPException) as exc_info:
            handler.get_thanks_received(12345, mock_request)

        assert exc_info.value.status_code == 404

    def test_get_thanks_sent_not_found(self, handler, mock_state):
        """Test get_thanks_sent raises 404 when user not found."""
        from models.data.rest_api.v1.entitybase.request import ThanksListRequest

        mock_state.vitess_client.user_repository.user_exists.return_value = False
        mock_request = ThanksListRequest(hours=24, limit=50, offset=0)

        with pytest.raises(HTTPException) as exc_info:
            handler.get_thanks_sent(12345, mock_request)

        assert exc_info.value.status_code == 404
