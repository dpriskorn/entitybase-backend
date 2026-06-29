"""Unit tests for thanks handler methods."""

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from datetime import datetime, timezone


class TestThanksHandlerMethods:
    """Test ThanksHandler methods with mocks."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        state.mysql_client = MagicMock()
        return state

    @pytest.fixture
    def handler(self, mock_state):
        """Create handler with mock state."""
        from models.rest_api.entitybase.v1.handlers.thanks import ThanksHandler

        handler = ThanksHandler(state=mock_state)
        return handler

    @pytest.fixture
    def mock_thank_item(self):
        """Create a mock thank item response."""
        from models.data.rest_api.v1.entitybase.response import ThankItemResponse

        return ThankItemResponse(
            id=1,
            from_user_id=42,
            to_user_id=7,
            entity_id="Q1",
            revision_id=123,
            created_at=datetime.now(timezone.utc),
        )

    def test_get_thanks_received_not_found(self, handler, mock_state):
        """Test get_thanks_received raises 404 when user not found."""
        from models.data.rest_api.v1.entitybase.request import ThanksListRequest

        mock_state.mysql_client.user_repository.user_exists.return_value = False
        mock_request = ThanksListRequest(hours=24, limit=50, offset=0)

        with pytest.raises(HTTPException) as exc_info:
            handler.get_thanks_received(12345, mock_request)

        assert exc_info.value.status_code == 404

    def test_get_thanks_received_error(self, handler, mock_state):
        """Test get_thanks_received raises 500 when repo fails."""
        from models.data.rest_api.v1.entitybase.request import ThanksListRequest

        mock_state.mysql_client.user_repository.user_exists.return_value = True
        mock_state.mysql_client.thanks_repository.get_thanks_received.return_value = (
            MagicMock(success=False, error="DB error")
        )
        mock_request = ThanksListRequest(hours=24, limit=50, offset=0)

        with pytest.raises(HTTPException) as exc_info:
            handler.get_thanks_received(1, mock_request)

        assert exc_info.value.status_code == 500

    def test_get_thanks_received_success(self, handler, mock_state, mock_thank_item):
        """Test get_thanks_received success path."""
        from models.data.rest_api.v1.entitybase.request import ThanksListRequest

        mock_state.mysql_client.user_repository.user_exists.return_value = True
        mock_state.mysql_client.thanks_repository.get_thanks_received.return_value = (
            MagicMock(
                success=True,
                data={
                    "thanks": [mock_thank_item],
                    "total_count": 1,
                    "has_more": False,
                },
            )
        )
        mock_request = ThanksListRequest(hours=24, limit=50, offset=0)

        result = handler.get_thanks_received(1, mock_request)

        assert result.user_id == 1
        assert result.total_count == 1

    def test_get_thanks_sent_not_found(self, handler, mock_state):
        """Test get_thanks_sent raises 404 when user not found."""
        from models.data.rest_api.v1.entitybase.request import ThanksListRequest

        mock_state.mysql_client.user_repository.user_exists.return_value = False
        mock_request = ThanksListRequest(hours=24, limit=50, offset=0)

        with pytest.raises(HTTPException) as exc_info:
            handler.get_thanks_sent(12345, mock_request)

        assert exc_info.value.status_code == 404

    def test_get_thanks_sent_error(self, handler, mock_state):
        """Test get_thanks_sent raises 500 when repo fails."""
        from models.data.rest_api.v1.entitybase.request import ThanksListRequest

        mock_state.mysql_client.user_repository.user_exists.return_value = True
        mock_state.mysql_client.thanks_repository.get_thanks_sent.return_value = (
            MagicMock(success=False, error="DB error")
        )
        mock_request = ThanksListRequest(hours=24, limit=50, offset=0)

        with pytest.raises(HTTPException) as exc_info:
            handler.get_thanks_sent(1, mock_request)

        assert exc_info.value.status_code == 500

    def test_get_thanks_sent_success(self, handler, mock_state, mock_thank_item):
        """Test get_thanks_sent success path."""
        from models.data.rest_api.v1.entitybase.request import ThanksListRequest

        mock_state.mysql_client.user_repository.user_exists.return_value = True
        mock_state.mysql_client.thanks_repository.get_thanks_sent.return_value = (
            MagicMock(
                success=True,
                data={
                    "thanks": [mock_thank_item],
                    "total_count": 1,
                    "has_more": False,
                },
            )
        )
        mock_request = ThanksListRequest(hours=24, limit=50, offset=0)

        result = handler.get_thanks_sent(1, mock_request)

        assert result.user_id == 1
        assert result.total_count == 1

    def test_send_thank_success(self, handler, mock_state, mock_thank_item):
        """Test send_thank success path."""
        from models.data.common import OperationResult

        mock_state.mysql_client.user_repository.user_exists.return_value = True
        mock_state.mysql_client.thanks_repository.send_thank_and_get.return_value = (
            OperationResult(success=True, data=mock_thank_item)
        )
        mock_state.mysql_client.user_repository.log_user_activity.return_value = (
            MagicMock(success=True)
        )

        result = handler.send_thank("Q1", 123, 42)

        assert result.from_user_id == 42
        assert result.entity_id == "Q1"

    def test_send_thank_user_not_found(self, handler, mock_state):
        """Test send_thank raises 404 when user not found."""
        mock_state.mysql_client.user_repository.user_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            handler.send_thank("Q1", 123, 999)

        assert exc_info.value.status_code == 404

    def test_send_thank_repo_failure(self, handler, mock_state):
        """Test send_thank raises 400 when repo fails."""
        from models.data.common import OperationResult

        mock_state.mysql_client.user_repository.user_exists.return_value = True
        mock_state.mysql_client.thanks_repository.send_thank_and_get.return_value = (
            OperationResult(success=False, error="Already thanked")
        )

        with pytest.raises(HTTPException) as exc_info:
            handler.send_thank("Q1", 123, 42)

        assert exc_info.value.status_code == 400

    def test_send_thank_send_and_get_failure(self, handler, mock_state):
        """Test send_thank raises 400 when send_thank_and_get returns failure."""
        from models.data.common import OperationResult

        mock_state.mysql_client.user_repository.user_exists.return_value = True
        mock_state.mysql_client.thanks_repository.send_thank_and_get.return_value = (
            OperationResult(success=False, error="Cannot thank your own revision")
        )

        with pytest.raises(HTTPException) as exc_info:
            handler.send_thank("Q1", 123, 42)

        assert exc_info.value.status_code == 400

    def test_send_thank_log_failure(self, handler, mock_state, mock_thank_item):
        """Test send_thank handles log_user_activity failure."""
        from models.data.common import OperationResult

        mock_state.mysql_client.user_repository.user_exists.return_value = True
        mock_state.mysql_client.thanks_repository.send_thank_and_get.return_value = (
            OperationResult(success=True, data=mock_thank_item)
        )
        mock_state.mysql_client.user_repository.log_user_activity.return_value = (
            MagicMock(success=False, error="Log failed")
        )

        result = handler.send_thank("Q1", 123, 42)

        assert result.from_user_id == 42
