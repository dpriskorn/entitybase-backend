import sys
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, "src")

from models.rest_api.request.user import UserCreateRequest
from models.rest_api.response.user import UserCreateResponse
from models.rest_api.handlers.user import UserHandler


class TestUserHandler:
    """Unit tests for UserHandler"""

    @pytest.fixture
    def mock_vitess_client(self) -> MagicMock:
        """Mock Vitess client"""
        client = MagicMock()
        client.user_repository = MagicMock()
        return client

    @pytest.fixture
    def handler(self) -> UserHandler:
        """Create handler instance"""
        return UserHandler()

    def test_create_user_new(
        self, handler: UserHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test creating a new user"""
        request = UserCreateRequest(user_id=12345)
        mock_vitess_client.user_repository.user_exists.return_value = False

        result = handler.create_user(request, mock_vitess_client)

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

        result = handler.create_user(request, mock_vitess_client)

        assert isinstance(result, UserCreateResponse)
        assert result.user_id == 12345
        assert result.created is False
        mock_vitess_client.user_repository.user_exists.assert_called_once_with(12345)
        mock_vitess_client.user_repository.create_user.assert_not_called()

    def test_get_user_found(
        self, handler: UserHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test getting a user that exists"""
        from models.user import User
        from datetime import datetime

        mock_user = User(
            user_id=12345, created_at=datetime(2023, 1, 1), preferences=None
        )
        mock_vitess_client.user_repository.get_user.return_value = mock_user

        result = handler.get_user(12345, mock_vitess_client)

        assert result == mock_user
        mock_vitess_client.user_repository.get_user.assert_called_once_with(12345)

    def test_get_user_not_found(
        self, handler: UserHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test getting a user that doesn't exist"""
        from fastapi import HTTPException

        mock_vitess_client.user_repository.get_user.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            handler.get_user(12345, mock_vitess_client)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User not found"
