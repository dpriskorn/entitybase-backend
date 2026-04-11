"""Unit tests for general_stats_worker."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from models.config.settings import settings
from models.data.rest_api.v1.entitybase.response.terms import (
    TermsByType,
    TermsPerLanguage,
)
from models.rest_api.entitybase.v1.services.general_stats_service import (
    GeneralStatsData,
)
from models.workers.general_stats.general_stats_worker import (
    GeneralStatsWorker,
)


class TestGeneralStatsWorker:
    """Unit tests for general_stats_worker."""

    def test_get_enabled_setting(self):
        """Test getting enabled setting."""
        worker = GeneralStatsWorker(vitess_client=MagicMock())
        assert worker.get_enabled_setting() == settings.general_stats_worker_enabled

    def test_get_schedule_setting(self):
        """Test getting schedule setting."""
        worker = GeneralStatsWorker(vitess_client=MagicMock())
        assert worker.get_schedule_setting() == settings.general_stats_schedule

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

    @pytest.mark.asyncio
    async def test_store_statistics_with_vitess_client(self):
        """Test storing statistics with vitess client."""
        mock_vitess_client = MagicMock()
        mock_vitess_client.user_repository = MagicMock()

        worker = GeneralStatsWorker(vitess_client=mock_vitess_client)

        stats = GeneralStatsData(
            total_statements=1000,
            total_qualifiers=500,
            total_references=300,
            total_items=100,
            total_lexemes=50,
            total_properties=25,
            total_sitelinks=200,
            total_terms=5000,
            terms_per_language=TermsPerLanguage(terms={"en": 1000}),
            terms_by_type=TermsByType(counts={"label": 5000}),
        )

        with patch(
            "models.workers.general_stats.general_stats_worker.date"
        ) as mock_date:
            mock_date.today.return_value.isoformat.return_value = "2024-01-01"

            await worker._store_statistics(stats)

            mock_vitess_client.user_repository.insert_general_statistics.assert_called_once()
