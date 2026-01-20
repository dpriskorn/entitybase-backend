import sys
from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.unit

sys.path.insert(0, "src")

from models.rest_api.entitybase.v1.request.user import UserCreateRequest
from models.rest_api.entitybase.v1.response.user import UserCreateResponse
from models.rest_api.entitybase.v1.handlers.user import UserHandler


class TestUserHandler:
    """Unit tests for UserHandler"""

    @pytest.fixture
    def mock_vitess_client(self) -> MagicMock:
        """Mock Vitess client"""
        client = MagicMock()
        client.user_repository = MagicMock()
        return client

    @pytest.fixture
    def handler(self, mock_vitess_client: MagicMock) -> UserHandler:
        """Create handler instance"""
        state = MagicMock()
        state.vitess_client = mock_vitess_client
        return UserHandler(state=state)

    def test_create_user_new(
        self, handler: UserHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test creating a new user"""
        request = UserCreateRequest(user_id=12345)

        mock_vitess_client.user_repository.user_exists.return_value = False

        result = handler.create_user(request)

        assert isinstance(result, UserCreateResponse)
        assert result.user_id == 12345
        assert result.created is True
        mock_vitess_client.user_repository.user_exists.assert_called_once_with(12345)
        mock_vitess_client.user_repository.create_user.assert_called_once_with(12345)

    def test_create_user_existing(
        self, handler: UserHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test creating a user that already exists"""
        request = UserCreateRequest(user_id=12345)

        mock_vitess_client.user_repository.user_exists.return_value = True

        result = handler.create_user(request)

        assert isinstance(result, UserCreateResponse)
        assert result.user_id == 12345
        assert result.created is False
        mock_vitess_client.user_repository.user_exists.assert_called_once_with(12345)
        mock_vitess_client.user_repository.create_user.assert_not_called()

    def test_get_user_found(
        self, handler: UserHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test getting a user that exists"""
        from models.rest_api.entitybase.v1.response.user import UserResponse
        from datetime import datetime

        mock_user = UserResponse(
            user_id=12345, created_at=datetime(2023, 1, 1), preferences=None
        )

        mock_vitess_client.user_repository.get_user.return_value = mock_user

        result = handler.get_user(12345)

        assert result == mock_user
        mock_vitess_client.user_repository.get_user.assert_called_once_with(12345)

    def test_get_user_not_found(
        self, handler: UserHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test getting a user that doesn't exist"""


        mock_vitess_client.user_repository.get_user.return_value = None

        with pytest.raises(ValueError) as exc_info:
            handler.get_user(12345)

        assert str(exc_info.value) == "User not found"

    def test_toggle_watchlist_success(
        self, handler: UserHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test successful watchlist toggle"""
        from models.rest_api.entitybase.v1.request.user import WatchlistToggleRequest
        from models.rest_api.entitybase.v1.response.user import WatchlistToggleResponse

        request = WatchlistToggleRequest(enabled=False)

        mock_vitess_client.user_repository.user_exists.return_value = True

        result = handler.toggle_watchlist(12345, request)

        assert isinstance(result, WatchlistToggleResponse)
        assert result.user_id == 12345
        assert result.enabled is False
        mock_vitess_client.user_repository.user_exists.assert_called_once_with(12345)
        mock_vitess_client.user_repository.set_watchlist_enabled.assert_called_once_with(
            12345, False
        )

    def test_toggle_watchlist_user_not_found(
        self, handler: UserHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test toggle for non-existent user"""
        from models.rest_api.entitybase.v1.request.user import WatchlistToggleRequest

        request = WatchlistToggleRequest(enabled=True)

        mock_vitess_client.user_repository.user_exists.return_value = False

        with pytest.raises(ValueError, match="User not registered"):
            handler.toggle_watchlist(12345, request)

        mock_vitess_client.user_repository.user_exists.assert_called_once_with(12345)
        mock_vitess_client.user_repository.set_watchlist_enabled.assert_not_called()
