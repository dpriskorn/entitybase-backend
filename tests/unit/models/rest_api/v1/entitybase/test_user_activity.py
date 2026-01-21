import sys
from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.unit

sys.path.insert(0, "src")

from models.rest_api.entitybase.v1.handlers.user_activity import UserActivityHandler
from models.rest_api.entitybase.v1.response.user_activity import (
    UserActivityResponse,
    UserActivityItemResponse,
)


class TestUserActivityHandler:
    """Unit tests for UserActivityHandler"""

    @pytest.fixture
    def mock_vitess_client(self) -> MagicMock:
        """Mock Vitess client"""
        client = MagicMock()
        client.user_repository = MagicMock()
        return client

    @pytest.fixture
    def handler(self, mock_vitess_client: MagicMock) -> UserActivityHandler:
        """Create handler instance"""
        state = MagicMock()
        state.vitess_client = mock_vitess_client
        return UserActivityHandler(state=state)

    def test_get_user_activities_success(
        self, handler: UserActivityHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test getting user activities successfully"""
        from datetime import datetime
        from models.rest_api.entitybase.v1.request.enums import UserActivityType

        mock_activity = UserActivityItemResponse(
            id=1,
            user_id=12345,
            activity_type=UserActivityType.ENTITY_REVERT,
            entity_id="Q42",
            revision_id=123,
            created_at=datetime(2023, 1, 1, 12, 0, 0),
        )

        mock_vitess_client.user_repository.user_exists.return_value = True
        from models.common import OperationResult

        mock_vitess_client.user_repository.get_user_activities.return_value = (
            OperationResult(success=True, data=[mock_activity])
        )

        result = handler.get_user_activities(12345, limit=30, offset=0)

        assert isinstance(result, UserActivityResponse)
        assert result.user_id == 12345
        assert len(result.activities) == 1
        assert isinstance(result.activities[0], UserActivityItemResponse)
        assert result.activities[0].id == 1

    def test_get_user_activities_user_not_found(
        self, handler: UserActivityHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test getting activities for non-existent user"""

        mock_vitess_client.user_repository.user_exists.return_value = False

        with pytest.raises(ValueError, match="User not registered"):
            handler.get_user_activities(12345)

    def test_get_user_activities_invalid_type(
        self, handler: UserActivityHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test getting activities with invalid type"""

        mock_vitess_client.user_repository.user_exists.return_value = True

        with pytest.raises(ValueError, match="Invalid activity type"):
            handler.get_user_activities(12345, activity_type="invalid")
