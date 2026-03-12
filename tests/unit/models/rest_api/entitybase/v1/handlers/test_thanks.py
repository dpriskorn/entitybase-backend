"""Unit tests for thanks handler."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone
from fastapi import HTTPException

from models.data.rest_api.v1.entitybase.request.thanks import ThanksListRequest


class TestThanksHandler:
    """Test ThanksHandler class."""

    @pytest.fixture
    def mock_thank(self):
        """Create a mock thank object."""
        thank = MagicMock()
        thank.id = 1
        thank.from_user_id = 1
        thank.to_user_id = 2
        thank.entity_id = "Q1"
        thank.revision_id = 123
        thank.created_at = datetime.now(timezone.utc)
        return thank

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        state.thanks_stream_producer = None
        return state

    @pytest.fixture
    def mock_handler(self, mock_state):
        """Create a mock handler with mocked state."""
        with patch(
            "models.rest_api.entitybase.v1.handlers.thanks.ThanksHandler"
        ) as MockHandler:
            handler = MagicMock()
            handler.state = mock_state
            return handler

    @pytest.mark.asyncio
    async def test_publish_thank_event_with_producer(self, mock_handler, mock_state):
        """Test _publish_thank_event when producer exists."""
        from models.rest_api.entitybase.v1.handlers.thanks import ThanksHandler

        mock_producer = AsyncMock()
        mock_state.thanks_stream_producer = mock_producer

        await ThanksHandler._publish_thank_event(
            mock_handler, 1, 2, "Q1", 123
        )

        mock_producer.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_thank_event_without_producer(self, mock_handler, mock_state):
        """Test _publish_thank_event when no producer exists."""
        from models.rest_api.entitybase.v1.handlers.thanks import ThanksHandler

        mock_state.thanks_stream_producer = None

        await ThanksHandler._publish_thank_event(
            mock_handler, 1, 2, "Q1", 123
        )

    def test_send_thank_user_not_found(self, mock_handler, mock_state):
        """Test send_thank raises error when user not found."""
        from models.rest_api.entitybase.v1.handlers.thanks import ThanksHandler

        mock_state.vitess_client.user_repository.user_exists.return_value = False

        handler = ThanksHandler(state=mock_state)

        with pytest.raises(HTTPException) as exc_info:
            handler.send_thank("Q1", 123, 999)

        assert exc_info.value.status_code == 404

    def test_send_thank_repository_failure(self, mock_handler, mock_state):
        """Test send_thank raises error when repository fails."""
        from models.rest_api.entitybase.v1.handlers.thanks import ThanksHandler

        mock_state.vitess_client.user_repository.user_exists.return_value = True
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "Database error"
        mock_state.vitess_client.thanks_repository.send_thank.return_value = mock_result

        handler = ThanksHandler(state=mock_state)

        with pytest.raises(HTTPException) as exc_info:
            handler.send_thank("Q1", 123, 1)

        assert exc_info.value.status_code == 400

    def test_send_thank_success(self, mock_handler, mock_state, mock_thank):
        """Test send_thank success case."""
        from models.rest_api.entitybase.v1.handlers.thanks import ThanksHandler

        mock_state.vitess_client.user_repository.user_exists.return_value = True

        mock_result = MagicMock()
        mock_result.success = True
        mock_state.vitess_client.thanks_repository.send_thank.return_value = mock_result

        mock_revision_result = MagicMock()
        mock_revision_result.success = True
        mock_revision_result.data = [mock_thank]
        mock_state.vitess_client.thanks_repository.get_revision_thanks.return_value = (
            mock_revision_result
        )

        mock_activity_result = MagicMock()
        mock_activity_result.success = True
        mock_state.vitess_client.user_repository.log_user_activity.return_value = (
            mock_activity_result
        )

        handler = ThanksHandler(state=mock_state)

        with patch.object(ThanksHandler, '_publish_thank_event', new_callable=AsyncMock):
            result = handler.send_thank("Q1", 123, 1)

        assert result.entity_id == "Q1"
        assert result.from_user_id == 1
        assert result.to_user_id == 2

    def test_get_thanks_received_user_not_found(self, mock_handler, mock_state):
        """Test get_thanks_received raises error when user not found."""
        from models.rest_api.entitybase.v1.handlers.thanks import ThanksHandler

        mock_state.vitess_client.user_repository.user_exists.return_value = False

        handler = ThanksHandler(state=mock_state)
        request = ThanksListRequest()

        with pytest.raises(HTTPException) as exc_info:
            handler.get_thanks_received(999, request)

        assert exc_info.value.status_code == 404

    def test_get_thanks_received_success(self, mock_handler, mock_state):
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

    def test_get_thanks_sent_user_not_found(self, mock_handler, mock_state):
        """Test get_thanks_sent raises error when user not found."""
        from models.rest_api.entitybase.v1.handlers.thanks import ThanksHandler

        mock_state.vitess_client.user_repository.user_exists.return_value = False

        handler = ThanksHandler(state=mock_state)
        request = ThanksListRequest()

        with pytest.raises(HTTPException) as exc_info:
            handler.get_thanks_sent(999, request)

        assert exc_info.value.status_code == 404

    def test_get_thanks_sent_success(self, mock_handler, mock_state):
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

    def test_get_revision_thanks_success(self, mock_handler, mock_state):
        """Test get_revision_thanks success case."""
        from models.rest_api.entitybase.v1.handlers.thanks import ThanksHandler

        mock_thank = MagicMock()
        mock_thank.id = 1
        mock_thank.from_user_id = 1
        mock_thank.to_user_id = 2

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = [mock_thank]
        mock_state.vitess_client.thanks_repository.get_revision_thanks.return_value = (
            mock_result
        )

        handler = ThanksHandler(state=mock_state)

        result = handler.get_revision_thanks("Q1", 123)

        assert result.entity_id == "Q1"
        assert result.revision_id == 123
        assert len(result.thanks) == 1

    def test_get_revision_thanks_failure(self, mock_handler, mock_state):
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
