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


class TestComputeDailyStats:
    """Unit tests for compute_daily_stats method."""

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

    def test_compute_daily_stats(self, service, mock_state):
        """Test compute_daily_stats method exists and is callable."""
        assert hasattr(service, "compute_daily_stats")
        assert callable(service.compute_daily_stats)


class TestExceptionHandling:
    """Unit tests for exception handling in stats methods."""

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

    def test_get_total_statements_exception(self, service, mock_state):
        """Test get_total_statements returns 0 on exception."""
        mock_state.vitess_client.cursor.__enter__.side_effect = Exception(
            "Table not found"
        )

        result = service.get_total_statements()
        assert result == 0

    def test_get_total_qualifiers_exception(self, service, mock_state):
        """Test get_total_qualifiers returns 0 on exception."""
        mock_state.vitess_client.cursor.__enter__.side_effect = Exception(
            "Table not found"
        )

        result = service.get_total_qualifiers()
        assert result == 0

    def test_get_total_references_exception(self, service, mock_state):
        """Test get_total_references returns 0 on exception."""
        mock_state.vitess_client.cursor.__enter__.side_effect = Exception(
            "Table not found"
        )

        result = service.get_total_references()
        assert result == 0

    def test_get_total_sitelinks_exception(self, service, mock_state):
        """Test get_total_sitelinks returns 0 on exception."""
        mock_state.vitess_client.cursor.__enter__.side_effect = Exception(
            "Table not found"
        )

        result = service.get_total_sitelinks()
        assert result == 0

    def test_get_total_terms_exception(self, service, mock_state):
        """Test get_total_terms returns 0 on exception."""
        mock_state.vitess_client.cursor.__enter__.side_effect = Exception(
            "Table not found"
        )

        result = service.get_total_terms()
        assert result == 0


class TestTermsPerLanguage:
    """Unit tests for get_terms_per_language method."""

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

    def test_get_terms_per_language_success(self, service, mock_state):
        """Test get_terms_per_language aggregates from all term tables."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [["en", 100], ["de", 50]],
            [["en", 80], ["de", 30]],
            [["en", 20], ["de", 10]],
        ]
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service.get_terms_per_language()

        assert result.terms["en"] == 200
        assert result.terms["de"] == 90

    def test_get_terms_per_language_partial_tables(self, service, mock_state):
        """Test get_terms_per_language handles missing tables gracefully."""
        call_count = 0

        def fetchall_side_effect():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("labels table not found")
            if call_count == 2:
                raise Exception("descriptions table not found")
            return [["en", 100]]

        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = fetchall_side_effect
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service.get_terms_per_language()

        assert result.terms["en"] == 100

    def test_get_terms_per_language_outer_exception(self, service, mock_state):
        """Test get_terms_per_language handles outer exception."""
        mock_state.vitess_client.cursor.__enter__.side_effect = Exception(
            "Connection error"
        )

        result = service.get_terms_per_language()
        assert result.terms == {}


class TestTermsByType:
    """Unit tests for get_terms_by_type method."""

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

    def test_get_terms_by_type_success(self, service, mock_state):
        """Test get_terms_by_type returns counts for each type."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            ["labels", 1000],
            ["descriptions", 500],
            ["aliases", 300],
        ]
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service.get_terms_by_type()

        assert result.counts["labels"] == 1000
        assert result.counts["descriptions"] == 500
        assert result.counts["aliases"] == 300

    def test_get_terms_by_type_partial_tables(self, service, mock_state):
        """Test get_terms_by_type handles missing tables gracefully."""
        call_count = 0

        def fetchone_side_effect():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("labels table not found")
            if call_count == 2:
                raise Exception("descriptions table not found")
            return ["aliases", 300]

        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = fetchone_side_effect
        mock_state.vitess_client.cursor.__enter__.return_value = mock_cursor

        result = service.get_terms_by_type()

        assert result.counts["aliases"] == 300
        assert "labels" not in result.counts

    def test_get_terms_by_type_outer_exception(self, service, mock_state):
        """Test get_terms_by_type handles outer exception."""
        mock_state.vitess_client.cursor.__enter__.side_effect = Exception(
            "Connection error"
        )

        result = service.get_terms_by_type()
        assert result.counts == {}
