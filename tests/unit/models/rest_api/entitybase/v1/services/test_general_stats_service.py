"""Unit tests for general stats service."""

import pytest
from unittest.mock import MagicMock


class TestGeneralStatsService:
    """Unit tests for GeneralStatsService."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object."""
        state = MagicMock()
        state.vitess_client = MagicMock()
        return state

    @pytest.fixture
    def service(self, mock_state):
        """Create service with mock state."""
        from models.rest_api.entitybase.v1.services.general_stats_service import (
            GeneralStatsService,
        )

        svc = GeneralStatsService(state=mock_state)
        return svc

    def test_get_total_statements(self, service, mock_state):
        """Test get_total_statements returns count."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [100]
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service.get_total_statements()
        assert result == 100

    def test_get_total_qualifiers(self, service, mock_state):
        """Test get_total_qualifiers returns count."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [50]
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service.get_total_qualifiers()
        assert result == 50

    def test_get_total_references(self, service, mock_state):
        """Test get_total_references returns count."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [25]
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service.get_total_references()
        assert result == 25

    def test_get_total_items(self, service, mock_state):
        """Test get_total_items returns count."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [200]
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service.get_total_items()
        assert result == 200

    def test_get_total_lexemes(self, service, mock_state):
        """Test get_total_lexemes returns count."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [75]
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service.get_total_lexemes()
        assert result == 75

    def test_get_total_properties(self, service, mock_state):
        """Test get_total_properties returns count."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [30]
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service.get_total_properties()
        assert result == 30

    def test_get_total_sitelinks(self, service, mock_state):
        """Test get_total_sitelinks returns count."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [150]
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service.get_total_sitelinks()
        assert result == 150

    def test_get_total_terms(self, service, mock_state):
        """Test get_total_terms returns count."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [500]
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service.get_total_terms()
        assert result == 500
