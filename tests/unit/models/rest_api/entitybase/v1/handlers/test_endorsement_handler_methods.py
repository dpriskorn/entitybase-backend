"""Unit tests for endorsements handler methods."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException
from datetime import datetime, timezone

from models.data.infrastructure.stream.actions import EndorseAction


class TestEndorsementHandlerMethods:
    """Test EndorsementHandler methods with mocks."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        state.vitess_client = MagicMock()
        state.endorsement_stream_producer = None
        return state

    @pytest.fixture
    def handler(self, mock_state):
        """Create handler with mock state."""
        from models.rest_api.entitybase.v1.handlers.endorsements import (
            EndorsementHandler,
        )

        handler = EndorsementHandler(state=mock_state)
        return handler

    @pytest.fixture
    def mock_endorsement(self):
        """Create a mock endorsement object for internal use."""
        from models.data.rest_api.v1.entitybase.response import (
            StatementEndorsementResponse,
        )

        return StatementEndorsementResponse(
            id=1,
            user_id=1,
            statement_hash=12345,
            created_at=datetime.now(timezone.utc),
        )

    def test_validate_user_not_found(self, handler, mock_state):
        """Test _validate_user raises 404 when user not found."""
        mock_state.vitess_client.user_repository.user_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            handler._validate_user(99999)

        assert exc_info.value.status_code == 404

    def test_handle_endorsement_error_not_found(self, handler):
        """Test _handle_endorsement_error with 'not found' in message."""
        with pytest.raises(HTTPException) as exc_info:
            handler._handle_endorsement_error("Endorsement not found", "create")

        assert exc_info.value.status_code == 404

    def test_handle_endorsement_error_other(self, handler):
        """Test _handle_endorsement_error with other error message."""
        with pytest.raises(HTTPException) as exc_info:
            handler._handle_endorsement_error("Already endorsed", "create")

        assert exc_info.value.status_code == 400

    def test_handle_endorsement_error_none(self, handler):
        """Test _handle_endorsement_error with None error."""
        with pytest.raises(HTTPException) as exc_info:
            handler._handle_endorsement_error(None, "create")

        assert exc_info.value.status_code == 400

    def test_find_endorsement_by_user_active_match(self, handler):
        """Test _find_endorsement_by_user finds active endorsement."""
        endorsement_active = MagicMock()
        endorsement_active.user_id = 1
        endorsement_active.removed_at = None

        result = handler._find_endorsement_by_user(
            [endorsement_active], 1, must_be_active=True
        )

        assert result == endorsement_active

    def test_find_endorsement_by_user_withdrawn_match(self, handler):
        """Test _find_endorsement_by_user finds withdrawn endorsement."""
        endorsement_withdrawn = MagicMock()
        endorsement_withdrawn.user_id = 1
        endorsement_withdrawn.removed_at = datetime.now(timezone.utc)

        result = handler._find_endorsement_by_user(
            [endorsement_withdrawn], 1, must_be_active=False
        )

        assert result == endorsement_withdrawn

    def test_find_endorsement_by_user_no_match(self, handler):
        """Test _find_endorsement_by_user raises when no match."""
        endorsement = MagicMock()
        endorsement.user_id = 2
        endorsement.removed_at = None

        with pytest.raises(HTTPException) as exc_info:
            handler._find_endorsement_by_user([endorsement], 1, must_be_active=True)

        assert exc_info.value.status_code == 500

    def test_get_and_validate_endorsement_success(
        self, handler, mock_state, mock_endorsement
    ):
        """Test _get_and_validate_endorsement success path."""
        mock_state.vitess_client.endorsement_repository.get_statement_endorsements.return_value = MagicMock(
            success=True,
            data={
                "endorsements": [mock_endorsement],
                "total_count": 1,
                "has_more": False,
            },
        )

        result = handler._get_and_validate_endorsement(12345, 1, must_be_active=True)

        assert result == mock_endorsement

    def test_get_and_validate_endorsement_failure(self, handler, mock_state):
        """Test _get_and_validate_endorsement when repo fails."""
        mock_state.vitess_client.endorsement_repository.get_statement_endorsements.return_value = MagicMock(
            success=False, error="DB error"
        )

        with pytest.raises(HTTPException) as exc_info:
            handler._get_and_validate_endorsement(12345, 1, must_be_active=True)

        assert exc_info.value.status_code == 500

    def test_get_and_validate_endorsement_no_data(self, handler, mock_state):
        """Test _get_and_validate_endorsement when no endorsements."""
        mock_state.vitess_client.endorsement_repository.get_statement_endorsements.return_value = MagicMock(
            success=True, data={"endorsements": []}
        )

        with pytest.raises(HTTPException) as exc_info:
            handler._get_and_validate_endorsement(12345, 1, must_be_active=True)

        assert exc_info.value.status_code == 500

    def test_get_statement_endorsements_success(self, handler, mock_state):
        """Test get_statement_endorsements success path."""
        mock_state.vitess_client.endorsement_repository.get_statement_endorsements.return_value = MagicMock(
            success=True,
            data={
                "endorsements": [
                    {
                        "id": 1,
                        "user_id": 1,
                        "hash": 12345,
                        "created_at": "2024-01-01T00:00:00Z",
                        "removed_at": "",
                    }
                ],
                "total_count": 1,
                "has_more": False,
            },
        )
        mock_state.vitess_client.endorsement_repository.get_batch_statement_endorsement_stats.return_value = MagicMock(
            success=True,
            data=[
                {
                    "total_endorsements": 5,
                    "active_endorsements": 3,
                    "withdrawn_endorsements": 2,
                }
            ],
        )

        from models.data.rest_api.v1.entitybase.request import EndorsementListRequest

        request = EndorsementListRequest(limit=10, offset=0, include_removed=False)
        result = handler.get_statement_endorsements(12345, request)

        assert result.statement_hash == 12345
        assert result.total_count == 1

    def test_get_statement_endorsements_error(self, handler, mock_state):
        """Test get_statement_endorsements when repo fails."""
        mock_state.vitess_client.endorsement_repository.get_statement_endorsements.return_value = MagicMock(
            success=False, error="Failed"
        )

        from models.data.rest_api.v1.entitybase.request import EndorsementListRequest

        request = EndorsementListRequest(limit=10, offset=0, include_removed=False)

        with pytest.raises(HTTPException) as exc_info:
            handler.get_statement_endorsements(12345, request)

        assert exc_info.value.status_code == 500

    def test_get_statement_endorsements_stats_error(self, handler, mock_state):
        """Test get_statement_endorsements when stats fails."""
        mock_state.vitess_client.endorsement_repository.get_statement_endorsements.return_value = MagicMock(
            success=True,
            data={"endorsements": [], "total_count": 0, "has_more": False},
        )
        mock_state.vitess_client.endorsement_repository.get_batch_statement_endorsement_stats.return_value = MagicMock(
            success=False, error="Stats failed"
        )

        from models.data.rest_api.v1.entitybase.request import EndorsementListRequest

        request = EndorsementListRequest(limit=10, offset=0, include_removed=False)

        with pytest.raises(HTTPException) as exc_info:
            handler.get_statement_endorsements(12345, request)

        assert exc_info.value.status_code == 500

    def test_get_statement_endorsements_no_stats_data(self, handler, mock_state):
        """Test get_statement_endorsements when stats data is empty."""
        mock_state.vitess_client.endorsement_repository.get_statement_endorsements.return_value = MagicMock(
            success=True,
            data={
                "endorsements": [
                    {
                        "id": 1,
                        "user_id": 1,
                        "hash": 12345,
                        "created_at": "2024-01-01T00:00:00Z",
                        "removed_at": "",
                    }
                ],
                "total_count": 1,
                "has_more": False,
            },
        )
        mock_state.vitess_client.endorsement_repository.get_batch_statement_endorsement_stats.return_value = MagicMock(
            success=True, data=None
        )

        from models.data.rest_api.v1.entitybase.request import EndorsementListRequest

        request = EndorsementListRequest(limit=10, offset=0, include_removed=False)
        result = handler.get_statement_endorsements(12345, request)

        assert result.stats.total == 0

    def test_get_user_endorsements_success(self, handler, mock_state):
        """Test get_user_endorsements success path."""
        mock_state.vitess_client.user_repository.user_exists.return_value = True
        mock_state.vitess_client.endorsement_repository.get_user_endorsements.return_value = MagicMock(
            success=True,
            data={
                "endorsements": [
                    {
                        "id": 1,
                        "user_id": 1,
                        "hash": 12345,
                        "created_at": "2024-01-01T00:00:00Z",
                        "removed_at": "",
                    }
                ],
                "total_count": 3,
                "has_more": True,
            },
        )

        from models.data.rest_api.v1.entitybase.request import EndorsementListRequest

        request = EndorsementListRequest(limit=10, offset=0, include_removed=False)
        result = handler.get_user_endorsements(1, request)

        assert result.user_id == 1
        assert result.total_count == 3
        assert result.has_more is True

    def test_get_user_endorsements_user_not_found(self, handler, mock_state):
        """Test get_user_endorsements when user not found."""
        mock_state.vitess_client.user_repository.user_exists.return_value = False

        from models.data.rest_api.v1.entitybase.request import EndorsementListRequest

        request = EndorsementListRequest(limit=10, offset=0, include_removed=False)

        with pytest.raises(HTTPException) as exc_info:
            handler.get_user_endorsements(99999, request)

        assert exc_info.value.status_code == 404

    def test_get_user_endorsements_error(self, handler, mock_state):
        """Test get_user_endorsements when repo fails."""
        mock_state.vitess_client.user_repository.user_exists.return_value = True
        mock_state.vitess_client.endorsement_repository.get_user_endorsements.return_value = MagicMock(
            success=False, error="Failed"
        )

        from models.data.rest_api.v1.entitybase.request import EndorsementListRequest

        request = EndorsementListRequest(limit=10, offset=0, include_removed=False)

        with pytest.raises(HTTPException) as exc_info:
            handler.get_user_endorsements(1, request)

        assert exc_info.value.status_code == 500

    def test_get_user_endorsement_stats_success(self, handler, mock_state):
        """Test get_user_endorsement_stats success path."""
        mock_state.vitess_client.user_repository.user_exists.return_value = True
        mock_state.vitess_client.endorsement_repository.get_user_endorsement_stats.return_value = MagicMock(
            success=True,
            data={"total_endorsements_given": 10, "total_endorsements_active": 5},
        )

        result = handler.get_user_endorsement_stats(1)

        assert result.user_id == 1
        assert result.total_endorsements_given == 10
        assert result.total_endorsements_active == 5

    def test_get_user_endorsement_stats_user_not_found(self, handler, mock_state):
        """Test get_user_endorsement_stats when user not found."""
        mock_state.vitess_client.user_repository.user_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            handler.get_user_endorsement_stats(99999)

        assert exc_info.value.status_code == 404

    def test_get_user_endorsement_stats_error(self, handler, mock_state):
        """Test get_user_endorsement_stats when repo fails."""
        mock_state.vitess_client.user_repository.user_exists.return_value = True
        mock_state.vitess_client.endorsement_repository.get_user_endorsement_stats.return_value = MagicMock(
            success=False, error="Failed"
        )

        with pytest.raises(HTTPException) as exc_info:
            handler.get_user_endorsement_stats(1)

        assert exc_info.value.status_code == 500

    def test_get_batch_statement_endorsement_stats_success(self, handler, mock_state):
        """Test get_batch_statement_endorsement_stats success."""
        mock_state.vitess_client.endorsement_repository.get_batch_statement_endorsement_stats.return_value = MagicMock(
            success=True,
            data=[
                {
                    "total_endorsements": 5,
                    "active_endorsements": 3,
                    "withdrawn_endorsements": 2,
                },
            ],
        )

        result = handler.get_batch_statement_endorsement_stats([12345])

        assert len(result.stats) == 1
        assert result.stats[0].total == 5

    def test_get_batch_statement_endorsement_stats_invalid_hash(self, handler):
        """Test get_batch_statement_endorsement_stats with invalid hash."""
        with pytest.raises(HTTPException) as exc_info:
            handler.get_batch_statement_endorsement_stats([0])

        assert exc_info.value.status_code == 400

    def test_get_batch_statement_endorsement_stats_error(self, handler, mock_state):
        """Test get_batch_statement_endorsement_stats when repo fails."""
        mock_state.vitess_client.endorsement_repository.get_batch_statement_endorsement_stats.return_value = MagicMock(
            success=False, error="Failed"
        )

        with pytest.raises(HTTPException) as exc_info:
            handler.get_batch_statement_endorsement_stats([1])

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_endorse_statement_success(
        self, handler, mock_state, mock_endorsement
    ):
        """Test endorse_statement success path."""
        mock_state.vitess_client.user_repository.user_exists.return_value = True
        mock_state.vitess_client.endorsement_repository.create_endorsement.return_value = MagicMock(
            success=True
        )
        mock_state.vitess_client.endorsement_repository.get_statement_endorsements.return_value = MagicMock(
            success=True,
            data={
                "endorsements": [mock_endorsement],
                "total_count": 1,
                "has_more": False,
            },
        )
        mock_state.vitess_client.user_repository.log_user_activity.return_value = (
            MagicMock(success=True)
        )

        result = await handler.endorse_statement(12345, 1)

        assert result.user_id == 1
        assert result.statement_hash == 12345

    @pytest.mark.asyncio
    async def test_endorse_statement_create_failure(self, handler, mock_state):
        """Test endorse_statement when create_endorsement fails."""
        mock_state.vitess_client.user_repository.user_exists.return_value = True
        mock_state.vitess_client.endorsement_repository.create_endorsement.return_value = MagicMock(
            success=False, error="Already endorsed"
        )

        with pytest.raises(HTTPException) as exc_info:
            await handler.endorse_statement(12345, 1)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_endorse_statement_log_failure(
        self, handler, mock_state, mock_endorsement
    ):
        """Test endorse_statement when log_user_activity fails."""
        mock_state.vitess_client.user_repository.user_exists.return_value = True
        mock_state.vitess_client.endorsement_repository.create_endorsement.return_value = MagicMock(
            success=True
        )
        mock_state.vitess_client.endorsement_repository.get_statement_endorsements.return_value = MagicMock(
            success=True,
            data={
                "endorsements": [mock_endorsement],
                "total_count": 1,
                "has_more": False,
            },
        )
        mock_state.vitess_client.user_repository.log_user_activity.return_value = (
            MagicMock(success=False, error="Log failed")
        )

        result = await handler.endorse_statement(12345, 1)

        assert result.statement_hash == 12345

    @pytest.mark.asyncio
    async def test_withdraw_endorsement_success(
        self, handler, mock_state, mock_endorsement
    ):
        """Test withdraw_endorsement success path."""
        mock_endorsement.removed_at = datetime.now(timezone.utc)
        mock_state.vitess_client.user_repository.user_exists.return_value = True
        mock_state.vitess_client.endorsement_repository.withdraw_endorsement.return_value = MagicMock(
            success=True
        )
        mock_state.vitess_client.endorsement_repository.get_statement_endorsements.return_value = MagicMock(
            success=True,
            data={
                "endorsements": [mock_endorsement],
                "total_count": 1,
                "has_more": False,
            },
        )
        mock_state.vitess_client.user_repository.log_user_activity.return_value = (
            MagicMock(success=True)
        )

        result = await handler.withdraw_endorsement(12345, 1)

        assert result.user_id == 1

    @pytest.mark.asyncio
    async def test_withdraw_endorsement_log_failure(
        self, handler, mock_state, mock_endorsement
    ):
        """Test withdraw_endorsement when log_user_activity fails."""
        mock_endorsement.removed_at = datetime.now(timezone.utc)
        mock_state.vitess_client.user_repository.user_exists.return_value = True
        mock_state.vitess_client.endorsement_repository.withdraw_endorsement.return_value = MagicMock(
            success=True
        )
        mock_state.vitess_client.endorsement_repository.get_statement_endorsements.return_value = MagicMock(
            success=True,
            data={
                "endorsements": [mock_endorsement],
                "total_count": 1,
                "has_more": False,
            },
        )
        mock_state.vitess_client.user_repository.log_user_activity.return_value = (
            MagicMock(success=False, error="Log failed")
        )

        result = await handler.withdraw_endorsement(12345, 1)

        assert result.user_id == 1

    @pytest.mark.asyncio
    async def test_withdraw_endorsement_failure(self, handler, mock_state):
        """Test withdraw_endorsement when withdrawal fails."""
        mock_state.vitess_client.user_repository.user_exists.return_value = True
        mock_state.vitess_client.endorsement_repository.withdraw_endorsement.return_value = MagicMock(
            success=False, error="Not found"
        )

        with pytest.raises(HTTPException) as exc_info:
            await handler.withdraw_endorsement(12345, 1)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_publish_endorsement_event_enabled(self, handler, mock_state):
        """Test _publish_endorsement_event when streaming is enabled."""
        mock_producer = AsyncMock()
        mock_state.endorsement_stream_producer = mock_producer
        with patch(
            "models.rest_api.entitybase.v1.handlers.endorsements.settings"
        ) as mock_settings:
            mock_settings.streaming_enabled = True
            await handler._publish_endorsement_event(12345, 1, EndorseAction.ENDORSE)

            mock_producer.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_endorsement_event_disabled(self, handler, mock_state):
        """Test _publish_endorsement_event when streaming is disabled."""
        await handler._publish_endorsement_event(12345, 1, EndorseAction.ENDORSE)
