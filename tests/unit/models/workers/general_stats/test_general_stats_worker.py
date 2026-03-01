"""Unit tests for general_stats_worker."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from models.workers.general_stats.general_stats_worker import (
    GeneralStatsWorker,
)


class TestGeneralStatsWorker:
    """Unit tests for general_stats_worker."""

    def test_get_enabled_setting(self):
        """Test getting enabled setting."""
        with patch(
            "models.workers.general_stats.general_stats_worker.settings"
        ) as mock_settings:
            mock_settings.general_stats_enabled = True
            worker = GeneralStatsWorker(vitess_client=MagicMock())
            assert worker.get_enabled_setting() is True

    def test_get_schedule_setting(self):
        """Test getting schedule setting."""
        with patch(
            "models.workers.general_stats.general_stats_worker.settings"
        ) as mock_settings:
            mock_settings.general_stats_schedule = "daily"
            worker = GeneralStatsWorker(vitess_client=MagicMock())
            assert worker.get_schedule_setting() == "daily"

    @pytest.mark.asyncio
    async def test_run_daily_computation_success(self):
        """Test successful daily computation."""
        mock_vitess_client = MagicMock()
        mock_service = MagicMock()
        mock_service.compute_daily_stats.return_value = MagicMock(
            total_statements=1000,
            total_qualifiers=500,
            total_references=300,
            total_items=100,
            total_lexemes=50,
            total_properties=25,
            total_sitelinks=200,
            total_terms=5000,
            terms_per_language=MagicMock(),
            terms_by_type=MagicMock(),
        )

        worker = GeneralStatsWorker(vitess_client=mock_vitess_client)
        worker._store_statistics = AsyncMock()

        with (
            patch(
                "models.workers.general_stats.general_stats_worker.GeneralStatsService",
                return_value=mock_service,
            ),
            patch(
                "models.workers.general_stats.general_stats_worker.settings"
            ) as mock_settings,
            patch(
                "models.workers.general_stats.general_stats_worker.datetime"
            ) as mock_datetime,
        ):
            mock_settings.general_stats_enabled = True
            mock_datetime.now.return_value = MagicMock()

            await worker.run_daily_computation()

            mock_service.compute_daily_stats.assert_called_once()
            worker._store_statistics.assert_called_once_with(
                mock_service.compute_daily_stats.return_value
            )
            assert worker.last_run is not None

    @pytest.mark.asyncio
    async def test_run_daily_computation_no_vitess_client(self):
        """Test daily computation with no vitess client."""
        worker = GeneralStatsWorker(vitess_client=None)

        with patch(
            "models.workers.general_stats.general_stats_worker.logger"
        ) as mock_logger:
            await worker.run_daily_computation()

            mock_logger.error.assert_called_once_with("Vitess client not initialized")

    @pytest.mark.asyncio
    async def test_run_daily_computation_exception(self):
        """Test daily computation with exception."""
        mock_vitess_client = MagicMock()

        worker = GeneralStatsWorker(vitess_client=mock_vitess_client)

        with (
            patch(
                "models.workers.general_stats.general_stats_worker.GeneralStatsService"
            ) as mock_service_class,
            patch(
                "models.workers.general_stats.general_stats_worker.logger"
            ) as mock_logger,
        ):
            mock_service_class.side_effect = Exception("Test error")

            with pytest.raises(Exception, match="Test error"):
                await worker.run_daily_computation()

            mock_logger.error.assert_called_once()
