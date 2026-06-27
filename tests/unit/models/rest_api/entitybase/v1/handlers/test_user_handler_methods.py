"""Unit tests for user handler methods."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException
from datetime import datetime, timezone


class TestUserHandlerMethods:
    """Test UserHandler methods with mocks."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        state.mysql_client = MagicMock()
        state.user_change_stream_producer = None
        return state

    @pytest.fixture
    def handler(self, mock_state):
        """Create handler with mock state."""
        from models.rest_api.entitybase.v1.handlers.user import UserHandler

        handler = UserHandler(state=mock_state)
        return handler

    @pytest.mark.asyncio
    async def test_create_user_new(self, handler, mock_state):
        """Test create_user creates a new user."""
        from models.data.rest_api.v1.entitybase.request import UserCreateRequest

        mock_state.mysql_client.user_repository.user_exists.return_value = False
        mock_state.mysql_client.user_repository.create_user.return_value = MagicMock(
            success=True
        )
        request = UserCreateRequest(user_id=42)

        result = await handler.create_user(request)

        assert result.user_id == 42
        assert result.created is True

    @pytest.mark.asyncio
    async def test_create_user_exists(self, handler, mock_state):
        """Test create_user when user already exists."""
        from models.data.rest_api.v1.entitybase.request import UserCreateRequest

        mock_state.mysql_client.user_repository.user_exists.return_value = True
        request = UserCreateRequest(user_id=42)

        result = await handler.create_user(request)

        assert result.user_id == 42
        assert result.created is False

    @pytest.mark.asyncio
    async def test_create_user_failure(self, handler, mock_state):
        """Test create_user when creation fails."""
        from models.data.rest_api.v1.entitybase.request import UserCreateRequest

        mock_state.mysql_client.user_repository.user_exists.return_value = False
        mock_state.mysql_client.user_repository.create_user.return_value = MagicMock(
            success=False, error="DB error"
        )
        request = UserCreateRequest(user_id=42)

        with pytest.raises(HTTPException) as exc_info:
            await handler.create_user(request)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_delete_user_success(self, handler, mock_state):
        """Test delete_user success."""
        mock_state.mysql_client.user_repository.user_exists.return_value = True
        mock_state.mysql_client.user_repository.delete_user.return_value = MagicMock(
            success=True
        )

        await handler.delete_user(42)

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, handler, mock_state):
        """Test delete_user when user not found."""
        mock_state.mysql_client.user_repository.user_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            await handler.delete_user(999)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_user_failure(self, handler, mock_state):
        """Test delete_user when deletion fails."""
        mock_state.mysql_client.user_repository.user_exists.return_value = True
        mock_state.mysql_client.user_repository.delete_user.return_value = MagicMock(
            success=False, error="DB error"
        )

        with pytest.raises(HTTPException) as exc_info:
            await handler.delete_user(42)

        assert exc_info.value.status_code == 500

    def test_get_user_success(self, handler, mock_state):
        """Test get_user success."""
        from models.data.rest_api.v1.entitybase.response import UserResponse

        from models.data.common.roles import UserRole

        user = UserResponse(
            user_id=1,
            username="testuser",
            role=UserRole.DEFAULT,
            created_at=datetime.now(timezone.utc),
        )
        mock_state.mysql_client.user_repository.get_user.return_value = user

        result = handler.get_user(1)

        assert result.user_id == 1

    def test_get_user_not_found(self, handler, mock_state):
        """Test get_user when user not found."""
        mock_state.mysql_client.user_repository.get_user.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            handler.get_user(999)

        assert exc_info.value.status_code == 404

    def test_get_user_wrong_type(self, handler, mock_state):
        """Test get_user when repo returns wrong type."""
        mock_state.mysql_client.user_repository.get_user.return_value = "not_a_user"

        with pytest.raises(HTTPException) as exc_info:
            handler.get_user(1)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_toggle_watchlist_enable(self, handler, mock_state):
        """Test toggle_watchlist enables watchlist."""
        from models.data.rest_api.v1.entitybase.request import WatchlistToggleRequest

        mock_state.mysql_client.user_repository.user_exists.return_value = True
        mock_state.mysql_client.user_repository.enable_watchlist.return_value = (
            MagicMock(success=True)
        )
        mock_request = WatchlistToggleRequest(enabled=True)

        result = await handler.toggle_watchlist(12345, mock_request)

        assert result.enabled is True

    @pytest.mark.asyncio
    async def test_toggle_watchlist_disable(self, handler, mock_state):
        """Test toggle_watchlist disables watchlist."""
        from models.data.rest_api.v1.entitybase.request import WatchlistToggleRequest

        mock_state.mysql_client.user_repository.user_exists.return_value = True
        mock_state.mysql_client.user_repository.disable_watchlist.return_value = (
            MagicMock(success=True)
        )
        mock_request = WatchlistToggleRequest(enabled=False)

        result = await handler.toggle_watchlist(12345, mock_request)

        assert result.enabled is False

    @pytest.mark.asyncio
    async def test_toggle_watchlist_not_found(self, handler, mock_state):
        """Test toggle_watchlist when user not found."""
        from models.data.rest_api.v1.entitybase.request import WatchlistToggleRequest

        mock_state.mysql_client.user_repository.user_exists.return_value = False
        mock_request = WatchlistToggleRequest(enabled=True)

        with pytest.raises(HTTPException) as exc_info:
            await handler.toggle_watchlist(999, mock_request)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_toggle_watchlist_error(self, handler, mock_state):
        """Test toggle_watchlist when repo fails."""
        from models.data.rest_api.v1.entitybase.request import WatchlistToggleRequest

        mock_state.mysql_client.user_repository.user_exists.return_value = True
        mock_state.mysql_client.user_repository.enable_watchlist.return_value = (
            MagicMock(success=False, error="DB error")
        )
        mock_request = WatchlistToggleRequest(enabled=True)

        with pytest.raises(HTTPException) as exc_info:
            await handler.toggle_watchlist(1, mock_request)

        assert exc_info.value.status_code == 500

    def test_get_user_stats_with_row(self, handler, mock_state):
        """Test get_user_stats with database row."""
        from datetime import date

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (date(2024, 1, 1), 100, 50)
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_state.mysql_client.connection_manager.acquire.return_value = (
            mock_connection
        )

        result = handler.get_user_stats()

        assert result.date == "2024-01-01"
        assert result.total_users == 100
        assert result.active_users == 50

    def test_get_user_stats_no_row(self, handler, mock_state):
        """Test get_user_stats compute fallback."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_state.mysql_client.connection_manager.acquire.return_value = (
            mock_connection
        )

        result = handler.get_user_stats()

        assert result.date == "live"

    @pytest.mark.asyncio
    async def test_publish_user_change_event_enabled(self, handler, mock_state):
        """Test _publish_user_change_event with streaming enabled."""
        from models.data.infrastructure.stream.change_type import ChangeType

        mock_producer = AsyncMock()
        mock_state.user_change_stream_producer = mock_producer
        with patch(
            "models.rest_api.entitybase.v1.handlers.user.settings"
        ) as mock_settings:
            mock_settings.streaming_enabled = True
            await handler._publish_user_change_event("42", ChangeType.USER_CREATION)

            mock_producer.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_user_change_event_disabled(self, handler, mock_state):
        """Test _publish_user_change_event when streaming is disabled."""
        from models.data.infrastructure.stream.change_type import ChangeType

        await handler._publish_user_change_event("42", ChangeType.USER_CREATION)

    def test_get_deduplication_statistics(self, handler, mock_state):
        """Test get_deduplication_statistics success."""
        mock_dedup = MagicMock()
        with patch(
            "models.rest_api.entitybase.v1.services.general_stats_service.GeneralStatsService"
        ) as MockService:
            MockService.return_value.compute_deduplication_stats.return_value = (
                mock_dedup
            )

            result = handler.get_deduplication_statistics()

            assert result == mock_dedup

    def test_parse_stats_terms_string_dict(self, handler):
        """Test _parse_stats_terms with string JSON dict."""
        from models.data.rest_api.v1.entitybase.response import TermsPerLanguage

        result = handler._parse_stats_terms('{"en": 10}', TermsPerLanguage)

        assert result.terms["en"] == 10

    def test_parse_stats_terms_terms_by_type(self, handler):
        """Test _parse_stats_terms with TermsByType."""
        from models.data.rest_api.v1.entitybase.response import TermsByType

        result = handler._parse_stats_terms('{"labels": 5}', TermsByType)

        assert result.counts["labels"] == 5

    def test_parse_stats_terms_empty_string(self, handler):
        """Test _parse_stats_terms with empty string."""
        from models.data.rest_api.v1.entitybase.response import TermsPerLanguage

        result = handler._parse_stats_terms("", TermsPerLanguage)

        assert result.terms == {}

    def test_parse_stats_terms_not_string(self, handler):
        """Test _parse_stats_terms with non-string data returns empty."""
        from models.data.rest_api.v1.entitybase.response import TermsPerLanguage

        result = handler._parse_stats_terms(42, TermsPerLanguage)

        assert result.terms == {}

    def test_parse_stats_terms_unknown_class(self, handler):
        """Test _parse_stats_terms with unknown response class."""
        result = handler._parse_stats_terms("{}", dict)

        assert result == {}

    def test_get_general_stats_with_row(self, handler, mock_state):
        """Test get_general_stats with database row."""
        from datetime import date

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (
            date(2024, 1, 1),
            100,
            10,
            5,
            200,
            50,
            30,
            150,
            300,
            '{"en": 200, "fr": 100}',
            '{"labels": 200, "descriptions": 100}',
        )
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_state.mysql_client.connection_manager.acquire.return_value = (
            mock_connection
        )

        result = handler.get_general_stats()

        assert result.date == "2024-01-01"
        assert result.total_statements == 100

    def test_get_general_stats_fallback(self, handler, mock_state):
        """Test get_general_stats compute fallback."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_state.mysql_client.connection_manager.acquire.return_value = (
            mock_connection
        )

        mock_stats = MagicMock()
        mock_stats.total_statements = 50
        mock_stats.total_qualifiers = 5
        mock_stats.total_references = 3
        mock_stats.total_items = 30
        mock_stats.total_lexemes = 10
        mock_stats.total_properties = 20
        mock_stats.total_sitelinks = 40
        mock_stats.total_terms = 100
        mock_stats.terms_per_language = {"en": 50}
        mock_stats.terms_by_type = {"labels": 50}

        with patch(
            "models.rest_api.entitybase.v1.services.general_stats_service.GeneralStatsService"
        ) as MockService:
            MockService.return_value.compute_daily_stats.return_value = mock_stats

            result = handler.get_general_stats()

            assert result.date == "live"
            assert result.total_statements == 50
