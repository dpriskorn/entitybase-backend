"""Unit tests for user_activity handler."""

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException


class TestUserActivityHandler:
    """Test UserActivityHandler class."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        return state

    @pytest.fixture
    def mock_handler(self, mock_state):
        """Create a mock handler with mocked state."""
        handler = MagicMock()
        handler.state = mock_state
        return handler

    def test_validate_user_success(self, mock_handler, mock_state):
        """Test _validate_user with valid user."""
        from models.rest_api.entitybase.v1.handlers.user_activity import UserActivityHandler
        mock_state.vitess_client.user_repository.user_exists.return_value = True

        UserActivityHandler._validate_user(mock_handler, 123)

        mock_state.vitess_client.user_repository.user_exists.assert_called_once_with(123)

    def test_validate_user_not_found(self, mock_handler, mock_state):
        """Test _validate_user with invalid user."""
        from models.rest_api.entitybase.v1.handlers.user_activity import UserActivityHandler
        mock_state.vitess_client.user_repository.user_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            UserActivityHandler._validate_user(mock_handler, 999)

        assert exc_info.value.status_code == 404
        assert "User not registered" in exc_info.value.detail

    def test_validate_parameters_valid(self, mock_handler):
        """Test _validate_parameters with valid parameters."""
        from models.rest_api.entitybase.v1.handlers.user_activity import UserActivityHandler

        # Should not raise
        UserActivityHandler._validate_parameters(mock_handler, "ENTITY_CREATE", 50)

    def test_validate_parameters_invalid_activity_type(self, mock_handler):
        """Test _validate_parameters with invalid activity_type."""
        from models.rest_api.entitybase.v1.handlers.user_activity import UserActivityHandler

        with pytest.raises(HTTPException) as exc_info:
            UserActivityHandler._validate_parameters(mock_handler, "INVALID_TYPE", 50)

        assert exc_info.value.status_code == 400

    def test_validate_parameters_invalid_limit(self, mock_handler):
        """Test _validate_parameters with invalid limit."""
        from models.rest_api.entitybase.v1.handlers.user_activity import UserActivityHandler

        with pytest.raises(HTTPException) as exc_info:
            UserActivityHandler._validate_parameters(mock_handler, None, 999)

        assert exc_info.value.status_code == 400
        assert "Limit must be one of" in exc_info.value.detail

    def test_validate_parameters_none_activity_type(self, mock_handler):
        """Test _validate_parameters with None activity_type (allowed)."""
        from models.rest_api.entitybase.v1.handlers.user_activity import UserActivityHandler

        # Should not raise
        UserActivityHandler._validate_parameters(mock_handler, None, 50)

    def test_parse_activity_type_with_valid_type(self, mock_handler):
        """Test _parse_activity_type with valid activity type."""
        from models.rest_api.entitybase.v1.handlers.user_activity import UserActivityHandler
        from models.data.rest_api.v1.entitybase.request.enums import UserActivityType

        result = UserActivityHandler._parse_activity_type(mock_handler, "entity_create")

        assert result == UserActivityType.ENTITY_CREATE

    def test_parse_activity_type_with_none(self, mock_handler):
        """Test _parse_activity_type with None."""
        from models.rest_api.entitybase.v1.handlers.user_activity import UserActivityHandler

        result = UserActivityHandler._parse_activity_type(mock_handler, None)

        assert result is None

    def test_parse_activity_type_with_invalid(self, mock_handler):
        """Test _parse_activity_type with invalid activity type."""
        from models.rest_api.entitybase.v1.handlers.user_activity import UserActivityHandler

        with pytest.raises(HTTPException) as exc_info:
            UserActivityHandler._parse_activity_type(mock_handler, "INVALID_TYPE")

        assert exc_info.value.status_code == 400

    def test_fetch_user_activities_success(self, mock_handler, mock_state):
        """Test _fetch_user_activities with successful result."""
        from models.rest_api.entitybase.v1.handlers.user_activity import UserActivityHandler
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = [{"id": 1}, {"id": 2}]
        mock_state.vitess_client.user_repository.get_user_activities.return_value = mock_result

        result = UserActivityHandler._fetch_user_activities(
            mock_handler, 123, None, 24, 50, 0
        )

        assert len(result) == 2
        mock_state.vitess_client.user_repository.get_user_activities.assert_called_once()

    def test_fetch_user_activities_failure(self, mock_handler, mock_state):
        """Test _fetch_user_activities with failed result."""
        from models.rest_api.entitybase.v1.handlers.user_activity import UserActivityHandler
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "Database error"
        mock_state.vitess_client.user_repository.get_user_activities.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            UserActivityHandler._fetch_user_activities(
                mock_handler, 123, None, 24, 50, 0
            )

        assert exc_info.value.status_code == 500

    def test_fetch_user_activities_none_data(self, mock_handler, mock_state):
        """Test _fetch_user_activities with None data."""
        from models.rest_api.entitybase.v1.handlers.user_activity import UserActivityHandler
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = None
        mock_state.vitess_client.user_repository.get_user_activities.return_value = mock_result

        result = UserActivityHandler._fetch_user_activities(
            mock_handler, 123, None, 24, 50, 0
        )

        assert result == []
