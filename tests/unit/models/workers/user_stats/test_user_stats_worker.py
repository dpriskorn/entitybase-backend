"""Unit tests for user_stats_worker."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from models.workers.user_stats.user_stats_worker import (
    UserStatsWorker,
)


class TestUserStatsWorker:
    """Unit tests for user_stats_worker."""

    def test_get_enabled_setting(self):
        """Test getting enabled setting."""
        with patch(
            "models.workers.user_stats.user_stats_worker.settings"
        ) as mock_settings:
            mock_settings.user_stats_enabled = True
            worker = UserStatsWorker(vitess_client=MagicMock())
            assert worker.get_enabled_setting() is True

    def test_get_schedule_setting(self):
        """Test getting schedule setting."""
        with patch(
            "models.workers.user_stats.user_stats_worker.settings"
        ) as mock_settings:
            mock_settings.user_stats_schedule = "daily"
            worker = UserStatsWorker(vitess_client=MagicMock())
            assert worker.get_schedule_setting() == "daily"

    @pytest.mark.asyncio
    async def test_run_daily_computation_success(self):
        """Test successful daily computation."""
        mock_vitess_client = MagicMock()
        mock_service = MagicMock()
        mock_service.compute_daily_stats.return_value = MagicMock(
            total_users=100, active_users=50
        )

        worker = UserStatsWorker(vitess_client=mock_vitess_client)
        worker._store_statistics = AsyncMock()

        with (
            patch(
                "models.workers.user_stats.user_stats_worker.UserStatsService",
                return_value=mock_service,
            ),
            patch(
                "models.workers.user_stats.user_stats_worker.settings"
            ) as mock_settings,
            patch(
                "models.workers.user_stats.user_stats_worker.datetime"
            ) as mock_datetime,
        ):
            mock_settings.user_stats_top_limit = 10
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
        worker = UserStatsWorker(vitess_client=None)

        with patch("models.workers.user_stats.user_stats_worker.logger") as mock_logger:
            await worker.run_daily_computation()

            mock_logger.error.assert_called_once_with("Vitess client not initialized")

    @pytest.mark.asyncio
    async def test_run_daily_computation_exception(self):
        """Test daily computation with exception."""
        mock_vitess_client = MagicMock()

        worker = UserStatsWorker(vitess_client=mock_vitess_client)

        with (
            patch(
                "models.workers.user_stats.user_stats_worker.UserStatsService"
            ) as mock_service_class,
            patch("models.workers.user_stats.user_stats_worker.logger") as mock_logger,
        ):
            mock_service_class.side_effect = Exception("Test error")

            with pytest.raises(Exception, match="Test error"):
                await worker.run_daily_computation()

            mock_logger.error.assert_called_once()
