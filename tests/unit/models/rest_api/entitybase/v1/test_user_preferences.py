import sys
from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.unit

sys.path.insert(0, "src")

from models.rest_api.entitybase.v1.handlers.user_preferences import (
    UserPreferencesHandler,
)
from models.data.rest_api.v1.entitybase.request.user_preferences import (
    UserPreferencesRequest,
)
from models.data.rest_api.v1.entitybase.response import (
    UserPreferencesResponse,
)


class TestUserPreferencesHandler:
    """Unit tests for UserPreferencesHandler"""

    @pytest.fixture
    def mock_vitess_client(self) -> MagicMock:
        """Mock Vitess client"""
        client = MagicMock()
        client.user_repository = MagicMock()
        return client

    @pytest.fixture
    def handler(self, mock_vitess_client: MagicMock) -> UserPreferencesHandler:
        """Create handler instance"""
        state = MagicMock()
        state.vitess_client = mock_vitess_client
        return UserPreferencesHandler(state=state)

    def test_get_preferences_success(
        self, handler: UserPreferencesHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test getting user preferences successfully"""
        mock_vitess_client.user_repository.user_exists.return_value = True
        from models.data.common import OperationResult

        mock_vitess_client.user_repository.get_user_preferences.return_value = (
            OperationResult(
                success=True,
                data={
                    "notification_limit": 100,
                    "retention_hours": 72,
                },
            )
        )

        result = handler.get_preferences(12345)

        assert isinstance(result, UserPreferencesResponse)
        assert result.user_id == 12345
        assert result.notification_limit == 100
        assert result.retention_hours == 72

    def test_get_preferences_defaults(
        self, handler: UserPreferencesHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test getting default preferences when none set"""
        mock_vitess_client.user_repository.user_exists.return_value = True
        from models.data.common import OperationResult

        mock_vitess_client.user_repository.get_user_preferences.return_value = (
            OperationResult(success=False, error="User preferences not found")
        )

        result = handler.get_preferences(12345)

        assert isinstance(result, UserPreferencesResponse)
        assert result.user_id == 12345
        assert result.notification_limit == 50  # default
        assert result.retention_hours == 24  # default

    def test_update_preferences_success(
        self, handler: UserPreferencesHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test updating preferences successfully"""
        request = UserPreferencesRequest(notification_limit=200, retention_hours=168)
        mock_vitess_client.user_repository.user_exists.return_value = True

        result = handler.update_preferences(12345, request)

        assert isinstance(result, UserPreferencesResponse)
        assert result.user_id == 12345
        assert result.notification_limit == 200
        assert result.retention_hours == 168
        mock_vitess_client.user_repository.update_user_preferences.assert_called_once_with(
            user_id=12345, notification_limit=200, retention_hours=168
        )

