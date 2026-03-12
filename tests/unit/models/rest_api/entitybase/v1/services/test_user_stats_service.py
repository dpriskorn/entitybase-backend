"""Unit tests for user_stats_service."""

import pytest
from unittest.mock import MagicMock


class TestUserStatsService:
    """Unit tests for UserStatsService."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        state.vitess_client = MagicMock()
        return state

    @pytest.fixture
    def service(self, mock_state):
        """Create service with mock state."""
        from models.rest_api.entitybase.v1.services.user_stats_service import (
            UserStatsService,
        )

        svc = UserStatsService(state=mock_state)
        return svc

    def test_get_total_users(self, service, mock_state):
        """Test get_total_users returns count."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [100]
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service.get_total_users()
        assert result == 100

    def test_get_active_users(self, service, mock_state):
        """Test get_active_users returns count."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [50]
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service.get_active_users()
        assert result == 50
