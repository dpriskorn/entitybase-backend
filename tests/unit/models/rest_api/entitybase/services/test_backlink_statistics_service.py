import pytest
from unittest.mock import MagicMock

pytestmark = pytest.mark.unit

from models.rest_api.entitybase.services.backlink_statistics_service import (
    BacklinkStatisticsService,
)


class TestBacklinkStatisticsService:
    def test_service_init_default(self):
        """Test service initialization with default values."""
        service = BacklinkStatisticsService()
        assert service.top_limit == 100

    def test_service_init_custom_limit(self):
        """Test service initialization with custom limit."""
        service = BacklinkStatisticsService(top_limit=50)
        assert service.top_limit == 50

    def test_compute_daily_stats(self):
        """Test computing daily statistics."""
        service = BacklinkStatisticsService()
        mock_vitess = MagicMock()

        # Mock the methods
        service.get_total_backlinks = MagicMock(return_value=1000)
        service.get_entities_with_backlinks = MagicMock(return_value=500)
        service.get_top_entities_by_backlinks = MagicMock(return_value=[])

        result = service.compute_daily_stats(mock_vitess)

        assert result.total_backlinks == 1000
        assert result.unique_entities_with_backlinks == 500
        assert result.top_entities_by_backlinks == []

        service.get_total_backlinks.assert_called_once_with(mock_vitess)
        service.get_entities_with_backlinks.assert_called_once_with(mock_vitess)
        service.get_top_entities_by_backlinks.assert_called_once_with(mock_vitess, 100)

    def test_get_total_backlinks(self):
        """Test getting total backlinks count."""
        service = BacklinkStatisticsService()
        mock_vitess = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_vitess.connection_manager.get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1234,)

        result = service.get_total_backlinks(mock_vitess)

        assert result == 1234
        mock_cursor.execute.assert_called_once_with(
            "SELECT COUNT(*) FROM entity_backlinks"
        )

    def test_get_total_backlinks_no_results(self):
        """Test getting total backlinks when no results."""
        service = BacklinkStatisticsService()
        mock_vitess = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_vitess.connection_manager.get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = service.get_total_backlinks(mock_vitess)

        assert result == 0

    def test_get_entities_with_backlinks(self):
        """Test getting count of entities with backlinks."""
        service = BacklinkStatisticsService()
        mock_vitess = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_vitess.connection_manager.get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (567,)

        result = service.get_entities_with_backlinks(mock_vitess)

        assert result == 567
        mock_cursor.execute.assert_called_once_with(
            "SELECT COUNT(DISTINCT referenced_internal_id) FROM entity_backlinks"
        )

    def test_get_top_entities_by_backlinks(self):
        """Test getting top entities by backlinks."""
        service = BacklinkStatisticsService()
        mock_vitess = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_vitess.connection_manager.get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock fetchall results
        mock_cursor.fetchall.return_value = [(123, 45), (456, 30)]
        mock_vitess.id_resolver.resolve_entity_id.side_effect = ["Q123", "Q456"]

        result = service.get_top_entities_by_backlinks(mock_vitess, 10)

        assert len(result) == 2
        assert result[0].entity_id == "Q123"
        assert result[0].backlink_count == 45
        assert result[1].entity_id == "Q456"
        assert result[1].backlink_count == 30

        mock_cursor.execute.assert_called_once()
        args, kwargs = mock_cursor.execute.call_args
        assert "LIMIT %s" in args[0]
        assert args[1] == (10,)

    def test_get_top_entities_by_backlinks_resolve_failure(self):
        """Test top entities when entity ID resolution fails."""
        service = BacklinkStatisticsService()
        mock_vitess = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_vitess.connection_manager.get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock fetchall results
        mock_cursor.fetchall.return_value = [(123, 45)]
        mock_vitess.id_resolver.resolve_entity_id.return_value = ""  # Resolution failed

        result = service.get_top_entities_by_backlinks(mock_vitess, 10)

        assert result == []  # Should skip unresolved entities
