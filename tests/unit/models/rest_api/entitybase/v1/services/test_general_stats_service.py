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


class TestDeduplicationStats:
    """Unit tests for deduplication stats methods."""

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

    def test_get_table_deduplication_stats_with_data(self, service, mock_state):
        """Test _get_table_deduplication_stats returns correct stats."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [100, 500]
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service._get_table_deduplication_stats("statements")

        assert result.unique_hashes == 100
        assert result.total_ref_count == 500
        assert result.deduplication_factor == 80.0
        assert result.space_saved == 400

    def test_get_table_deduplication_stats_no_data(self, service, mock_state):
        """Test _get_table_deduplication_stats returns zeros when no data."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [0, 0]
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service._get_table_deduplication_stats("statements")

        assert result.unique_hashes == 0
        assert result.total_ref_count == 0
        assert result.deduplication_factor == 0.0
        assert result.space_saved == 0

    def test_get_table_deduplication_stats_exception(self, service, mock_state):
        """Test _get_table_deduplication_stats handles exceptions."""
        mock_state.vitess_client.cursor.__enter__.side_effect = Exception(
            "Table not found"
        )

        result = service._get_table_deduplication_stats("nonexistent_table")

        assert result.unique_hashes == 0
        assert result.total_ref_count == 0
        assert result.deduplication_factor == 0.0

    def test_get_terms_deduplication_stats(self, service, mock_state):
        """Test _get_terms_deduplication_stats aggregates across tables."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            [50, 100],
            [30, 60],
            [20, 40],
        ]
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service._get_terms_deduplication_stats()

        assert result.unique_hashes == 100
        assert result.total_ref_count == 200
        assert result.deduplication_factor == 50.0
        assert result.space_saved == 100

    def test_get_terms_deduplication_stats_no_tables(self, service, mock_state):
        """Test _get_terms_deduplication_stats when tables don't exist."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Table not found")
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service._get_terms_deduplication_stats()

        assert result.unique_hashes == 0
        assert result.total_ref_count == 0

    def test_compute_deduplication_stats(self, service, mock_state):
        """Test compute_deduplication_stats returns stats for all types."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            [100, 500],
            [80, 400],
            [60, 300],
            [40, 200],
            [30, 150],
            [50, 100],
            [30, 60],
            [20, 40],
        ]
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service.compute_deduplication_stats()

        assert result.statements.unique_hashes == 100
        assert result.qualifiers.unique_hashes == 80
        assert result.references.unique_hashes == 60
        assert result.snaks.unique_hashes == 40
        assert result.sitelinks.unique_hashes == 30
        assert result.terms.unique_hashes == 100
