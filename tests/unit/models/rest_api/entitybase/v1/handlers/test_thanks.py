"""Unit tests for thanks handler."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from fastapi import HTTPException

from models.data.rest_api.v1.entitybase.request.thanks import ThanksListRequest


class TestThanksHandler:
    """Test ThanksHandler class."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        state.thanks_stream_producer = None
        return state

    def test_get_thanks_received_user_not_found(self, mock_state):
        """Test get_thanks_received raises error when user not found."""
        from models.rest_api.entitybase.v1.handlers.thanks import ThanksHandler

        mock_state.vitess_client.user_repository.user_exists.return_value = False

        handler = ThanksHandler(state=mock_state)
        request = ThanksListRequest()

        with pytest.raises(HTTPException) as exc_info:
            handler.get_thanks_received(999, request)

        assert exc_info.value.status_code == 404

    def test_get_thanks_received_success(self, mock_state):
        """Test get_thanks_received success case."""
        from models.rest_api.entitybase.v1.handlers.thanks import ThanksHandler

        mock_state.vitess_client.user_repository.user_exists.return_value = True

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = {
            "thanks": [],
            "total_count": 0,
            "has_more": False,
        }
        mock_state.vitess_client.thanks_repository.get_thanks_received.return_value = (
            mock_result
        )

        handler = ThanksHandler(state=mock_state)
        request = ThanksListRequest()

        result = handler.get_thanks_received(1, request)

        assert result.user_id == 1
        assert result.total_count == 0

    def test_get_thanks_sent_user_not_found(self, mock_state):
        """Test get_thanks_sent raises error when user not found."""
        from models.rest_api.entitybase.v1.handlers.thanks import ThanksHandler

        mock_state.vitess_client.user_repository.user_exists.return_value = False

        handler = ThanksHandler(state=mock_state)
        request = ThanksListRequest()

        with pytest.raises(HTTPException) as exc_info:
            handler.get_thanks_sent(999, request)

        assert exc_info.value.status_code == 404

    def test_get_thanks_sent_success(self, mock_state):
        """Test get_thanks_sent success case."""
        from models.rest_api.entitybase.v1.handlers.thanks import ThanksHandler

        mock_state.vitess_client.user_repository.user_exists.return_value = True

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = {
            "thanks": [],
            "total_count": 0,
            "has_more": False,
        }
        mock_state.vitess_client.thanks_repository.get_thanks_sent.return_value = (
            mock_result
        )

        handler = ThanksHandler(state=mock_state)
        request = ThanksListRequest()

        result = handler.get_thanks_sent(1, request)

        assert result.user_id == 1
        assert result.total_count == 0

    def test_get_revision_thanks_success(self, mock_state):
        """Test get_revision_thanks success case."""
        from models.rest_api.entitybase.v1.handlers.thanks import ThanksHandler

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = [
            {
                "id": 1,
                "from_user_id": 1,
                "to_user_id": 2,
                "entity_id": "Q1",
                "revision_id": 123,
                "created_at": datetime.now(timezone.utc),
            }
        ]
        mock_state.vitess_client.thanks_repository.get_revision_thanks.return_value = (
            mock_result
        )

        handler = ThanksHandler(state=mock_state)

        result = handler.get_revision_thanks("Q1", 123)

        assert result.user_id == 0
        assert result.total_count == 1

    def test_get_revision_thanks_failure(self, mock_state):
        """Test get_revision_thanks raises error on failure."""
        from models.rest_api.entitybase.v1.handlers.thanks import ThanksHandler

        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "Database error"
        mock_state.vitess_client.thanks_repository.get_revision_thanks.return_value = (
            mock_result
        )

        handler = ThanksHandler(state=mock_state)

        with pytest.raises(HTTPException) as exc_info:
            handler.get_revision_thanks("Q1", 123)

        assert exc_info.value.status_code == 500
