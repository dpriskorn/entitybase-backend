"""Unit tests for BacklinkStatisticsService."""

import pytest
from unittest.mock import MagicMock, patch


class TestBacklinkStatisticsService:
    """Unit tests for BacklinkStatisticsService."""

    def test_compute_daily_stats(self):
        """Test computing daily backlink statistics."""
        from models.rest_api.entitybase.v1.services.backlink_statistics_service import (
            BacklinkStatisticsService,
        )

        mock_state = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [100]
        mock_cursor.fetchall.return_value = []
        mock_state.vitess_client.cursor = mock_cursor
        mock_state.vitess_client.id_resolver = MagicMock()

        service = BacklinkStatisticsService(state=mock_state)
        service.top_limit = 10

        result = service.compute_daily_stats()

        assert result.total_backlinks == 100

    def test_get_total_backlinks(self):
        """Test getting total backlink count."""
        from models.rest_api.entitybase.v1.services.backlink_statistics_service import (
            BacklinkStatisticsService,
        )

        mock_state = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [150]
        mock_state.vitess_client.cursor = mock_cursor

        service = BacklinkStatisticsService(state=mock_state)

        result = service.get_total_backlinks()

        assert result == 150
        mock_cursor.execute.assert_called_once()

    def test_get_total_backlinks_no_results(self):
        """Test getting total backlinks when none exist."""
        from models.rest_api.entitybase.v1.services.backlink_statistics_service import (
            BacklinkStatisticsService,
        )

        mock_state = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_state.vitess_client.cursor = mock_cursor

        service = BacklinkStatisticsService(state=mock_state)

        result = service.get_total_backlinks()

        assert result == 0

    def test_get_entities_with_backlinks(self):
        """Test getting count of entities with backlinks."""
        from models.rest_api.entitybase.v1.services.backlink_statistics_service import (
            BacklinkStatisticsService,
        )

        mock_state = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [50]
        mock_state.vitess_client.cursor = mock_cursor

        service = BacklinkStatisticsService(state=mock_state)

        result = service.get_entities_with_backlinks()

        assert result == 50

    def test_get_top_entities_by_backlinks(self):
        """Test getting top entities by backlink count."""
        from models.rest_api.entitybase.v1.services.backlink_statistics_service import (
            BacklinkStatisticsService,
        )

        mock_state = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, 100),
            (2, 50),
        ]
        mock_state.vitess_client.cursor = mock_cursor

        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_entity_id.side_effect = lambda internal_id: {
            1: "Q1",
            2: "Q2",
        }.get(internal_id)
        mock_state.vitess_client.id_resolver = mock_id_resolver

        service = BacklinkStatisticsService(state=mock_state)

        result = service.get_top_entities_by_backlinks(limit=10)

        assert len(result) == 2
        assert result[0].entity_id == "Q1"
        assert result[0].backlink_count == 100
        assert result[1].entity_id == "Q2"
        assert result[1].backlink_count == 50

    def test_get_top_entities_by_backlinks_empty(self):
        """Test getting top entities when none exist."""
        from models.rest_api.entitybase.v1.services.backlink_statistics_service import (
            BacklinkStatisticsService,
        )

        mock_state = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_state.vitess_client.cursor = mock_cursor
        mock_state.vitess_client.id_resolver = MagicMock()

        service = BacklinkStatisticsService(state=mock_state)

        result = service.get_top_entities_by_backlinks(limit=10)

        assert result == []

    def test_top_limit_parameter(self):
        """Test that top_limit parameter is respected."""
        from models.rest_api.entitybase.v1.services.backlink_statistics_service import (
            BacklinkStatisticsService,
        )

        mock_state = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_state.vitess_client.cursor = mock_cursor
        mock_state.vitess_client.id_resolver = MagicMock()

        service = BacklinkStatisticsService(state=mock_state, top_limit=50)

        service.get_top_entities_by_backlinks()

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1] == (50,)

    def test_compute_daily_stats_full_flow(self):
        """Test full daily stats computation flow."""
        from models.rest_api.entitybase.v1.services.backlink_statistics_service import (
            BacklinkStatisticsService,
        )

        mock_state = MagicMock()

        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [[100], [50]]
        mock_cursor.fetchall.return_value = [(1, 100), (2, 50)]
        mock_state.vitess_client.cursor = mock_cursor

        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_entity_id.side_effect = lambda internal_id: {
            1: "Q1",
            2: "Q2",
        }.get(internal_id)
        mock_state.vitess_client.id_resolver = mock_id_resolver

        service = BacklinkStatisticsService(state=mock_state)

        result = service.compute_daily_stats()

        assert result.total_backlinks == 100
        assert result.unique_entities_with_backlinks == 50
        assert len(result.top_entities_by_backlinks) == 2
