"""Unit tests for user_preferences.py."""

from unittest.mock import AsyncMock, MagicMock
import pytest

from models.data.rest_api.v1.entitybase.request.user_preferences import (
    UserPreferencesRequest,
)
from models.rest_api.entitybase.v1.handlers.user_preferences import (
    UserPreferencesHandler,
)


class TestUserPreferencesHandlerGetPreferences:
    """Tests for UserPreferencesHandler.get_preferences."""

    @pytest.fixture
    def mock_state(self) -> MagicMock:
        state = MagicMock()
        state.vitess_client.user_repository.user_exists.return_value = True
        return state

    @pytest.fixture
    def handler(self, mock_state: MagicMock) -> UserPreferencesHandler:
        return UserPreferencesHandler(state=mock_state)

    def test_get_preferences_user_not_found(self) -> None:
        mock_state = MagicMock()
        mock_state.vitess_client.user_repository.user_exists.return_value = False
        handler = UserPreferencesHandler(state=mock_state)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            handler.get_preferences(99999)
        assert exc_info.value.status_code == 404

    def test_get_preferences_success(
        self, handler: UserPreferencesHandler, mock_state: MagicMock
    ) -> None:
        mock_state.vitess_client.user_repository.get_user_preferences.return_value = (
            MagicMock(
                success=True,
                data={"notification_limit": 100, "retention_hours": 48},
            )
        )

        result = handler.get_preferences(123)

        assert result.user_id == 123
        assert result.notification_limit == 100
        assert result.retention_hours == 48

    def test_get_preferences_not_found_in_error(
        self, handler: UserPreferencesHandler, mock_state: MagicMock
    ) -> None:
        mock_state.vitess_client.user_repository.get_user_preferences.return_value = (
            MagicMock(
                success=False,
                error="User preferences not found",
                data=None,
            )
        )

        result = handler.get_preferences(123)

        assert result.user_id == 123
        assert result.notification_limit == 50
        assert result.retention_hours == 24

    def test_get_preferences_data_none(
        self, handler: UserPreferencesHandler, mock_state: MagicMock
    ) -> None:
        mock_state.vitess_client.user_repository.get_user_preferences.return_value = (
            MagicMock(
                success=True,
                data=None,
            )
        )

        result = handler.get_preferences(123)

        assert result.user_id == 123
        assert result.notification_limit == 50
        assert result.retention_hours == 24

    def test_get_preferences_data_not_dict(
        self, handler: UserPreferencesHandler, mock_state: MagicMock
    ) -> None:
        mock_state.vitess_client.user_repository.get_user_preferences.return_value = (
            MagicMock(
                success=True,
                data="not a dict",
            )
        )

        result = handler.get_preferences(123)

        assert result.user_id == 123
        assert result.notification_limit == 50
        assert result.retention_hours == 24

    def test_get_preferences_other_error(
        self, handler: UserPreferencesHandler, mock_state: MagicMock
    ) -> None:
        mock_state.vitess_client.user_repository.get_user_preferences.return_value = (
            MagicMock(
                success=False,
                error="Database connection failed",
                data=None,
            )
        )

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            handler.get_preferences(123)
        assert exc_info.value.status_code == 500


class TestUserPreferencesHandlerUpdatePreferences:
    """Tests for UserPreferencesHandler.update_preferences."""

    @pytest.fixture
    def mock_state(self) -> MagicMock:
        state = MagicMock()
        state.vitess_client.user_repository.user_exists.return_value = True
        state.vitess_client.user_repository.update_user_preferences.return_value = (
            MagicMock(success=True)
        )
        state.user_change_stream_producer = MagicMock()
        state.user_change_stream_producer.publish = AsyncMock()
        return state

    @pytest.fixture
    def handler(self, mock_state: MagicMock) -> UserPreferencesHandler:
        return UserPreferencesHandler(state=mock_state)

    @pytest.mark.asyncio
    async def test_update_preferences_user_not_found(self) -> None:
        mock_state = MagicMock()
        mock_state.vitess_client.user_repository.user_exists.return_value = False
        handler = UserPreferencesHandler(state=mock_state)

        request = UserPreferencesRequest(notification_limit=100, retention_hours=48)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await handler.update_preferences(123, request)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_preferences_success(
        self, handler: UserPreferencesHandler, mock_state: MagicMock
    ) -> None:
        request = UserPreferencesRequest(notification_limit=100, retention_hours=48)

        result = await handler.update_preferences(123, request)

        assert result.user_id == 123
        assert result.notification_limit == 100
        assert result.retention_hours == 48
        mock_state.vitess_client.user_repository.update_user_preferences.assert_called_once_with(
            user_id=123, notification_limit=100, retention_hours=48
        )

    @pytest.mark.asyncio
    async def test_update_preferences_failure(
        self, handler: UserPreferencesHandler, mock_state: MagicMock
    ) -> None:
        mock_state.vitess_client.user_repository.update_user_preferences.return_value = MagicMock(
            success=False, error="Update failed"
        )
        request = UserPreferencesRequest(notification_limit=100, retention_hours=48)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await handler.update_preferences(123, request)
        assert exc_info.value.status_code == 500
