"""Unit tests for backlink_statistics_worker."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from models.workers.backlink_statistics.backlink_statistics_worker import BacklinkStatisticsWorker


class TestBacklinkStatisticsWorker:
    """Unit tests for backlink_statistics_worker."""

    def test_get_enabled_setting(self):
        """Test getting enabled setting."""
        with patch('models.workers.backlink_statistics.backlink_statistics_worker.settings') as mock_settings:
            mock_settings.backlink_stats_enabled = True
            worker = BacklinkStatisticsWorker(vitess_client=MagicMock())
            assert worker.get_enabled_setting() is True

    def test_get_schedule_setting(self):
        """Test getting schedule setting."""
        with patch('models.workers.backlink_statistics.backlink_statistics_worker.settings') as mock_settings:
            mock_settings.backlink_stats_schedule = "daily"
            worker = BacklinkStatisticsWorker(vitess_client=MagicMock())
            assert worker.get_schedule_setting() == "daily"

    @pytest.mark.asyncio
    async def test_run_daily_computation_success(self):
        """Test successful daily computation."""
        mock_vitess_client = MagicMock()
        mock_service = MagicMock()
        mock_service.compute_daily_stats.return_value = MagicMock(
            total_backlinks=100,
            unique_entities_with_backlinks=50
        )

        worker = BacklinkStatisticsWorker(vitess_client=mock_vitess_client)
        worker._store_statistics = AsyncMock()

        with patch('models.workers.backlink_statistics.backlink_statistics_worker.BacklinkStatisticsService', return_value=mock_service), \
             patch('models.workers.backlink_statistics.backlink_statistics_worker.settings') as mock_settings, \
             patch('models.workers.backlink_statistics.backlink_statistics_worker.datetime') as mock_datetime:

            mock_settings.backlink_stats_top_limit = 10
            mock_datetime.now.return_value = MagicMock()

            await worker.run_daily_computation()

            mock_service.compute_daily_stats.assert_called_once()
            worker._store_statistics.assert_called_once_with(mock_service.compute_daily_stats.return_value)
            assert worker.last_run is not None

    @pytest.mark.asyncio
    async def test_run_daily_computation_no_vitess_client(self):
        """Test daily computation with no vitess client."""
        worker = BacklinkStatisticsWorker(vitess_client=None)

        with patch('models.workers.backlink_statistics.backlink_statistics_worker.logger') as mock_logger:
            await worker.run_daily_computation()

            mock_logger.error.assert_called_once_with("Vitess client not initialized")

    @pytest.mark.asyncio
    async def test_run_daily_computation_exception(self):
        """Test daily computation with exception."""
        mock_vitess_client = MagicMock()

        worker = BacklinkStatisticsWorker(vitess_client=mock_vitess_client)

        with patch('models.workers.backlink_statistics.backlink_statistics_worker.BacklinkStatisticsService') as mock_service_class, \
             patch('models.workers.backlink_statistics.backlink_statistics_worker.logger') as mock_logger:

            mock_service_class.side_effect = Exception("Test error")

            with pytest.raises(Exception, match="Test error"):
                await worker.run_daily_computation()

            mock_logger.error.assert_called_once()
