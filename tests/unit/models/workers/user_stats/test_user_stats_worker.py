"""Unit tests for user_stats_worker."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from models.config.settings import settings
from models.data.rest_api.v1.entitybase.response import UserStatsData
from models.workers.user_stats.user_stats_worker import (
    UserStatsWorker,
)


class TestUserStatsWorker:
    """Unit tests for user_stats_worker."""

    def test_get_enabled_setting(self):
        """Test getting enabled setting."""
        worker = UserStatsWorker(vitess_client=MagicMock())
        assert worker.get_enabled_setting() == settings.user_stats_worker_enabled

    def test_get_schedule_setting(self):
        """Test getting schedule setting."""
        worker = UserStatsWorker(vitess_client=MagicMock())
        assert worker.get_schedule_setting() == settings.user_stats_schedule

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

    @pytest.mark.asyncio
    async def test_store_statistics_with_vitess_client(self):
        """Test storing statistics with vitess client."""
        mock_vitess_client = MagicMock()
        mock_vitess_client.user_repository = MagicMock()

        worker = UserStatsWorker(vitess_client=mock_vitess_client)

        stats = UserStatsData(
            total_users=100,
            active_users=50,
        )

        with patch("models.workers.user_stats.user_stats_worker.date") as mock_date:
            mock_date.today.return_value.isoformat.return_value = "2024-01-01"

            await worker._store_statistics(stats)

            mock_vitess_client.user_repository.insert_user_statistics.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_statistics_no_vitess_client(self):
        """Test storing statistics without vitess client returns early."""
        worker = UserStatsWorker(vitess_client=None)

        await worker._store_statistics(MagicMock())

    @pytest.mark.asyncio
    async def test_run_server_no_uvicorn(self):
        """Test run_server raises RuntimeError when uvicorn is None."""
        from models.workers.user_stats.user_stats_worker import run_server

        with patch("models.workers.user_stats.user_stats_worker.uvicorn", None):
            with pytest.raises(RuntimeError, match="uvicorn not installed"):
                await run_server(MagicMock())

    @pytest.mark.asyncio
    async def test_run_server_success(self):
        """Test run_server starts uvicorn server."""
        from models.workers.user_stats.user_stats_worker import run_server

        mock_uvicorn = MagicMock()
        mock_server = MagicMock()
        mock_server.serve = AsyncMock()
        mock_uvicorn.Config.return_value = MagicMock()
        mock_uvicorn.Server.return_value = mock_server

        with patch("models.workers.user_stats.user_stats_worker.uvicorn", mock_uvicorn):
            await run_server(MagicMock())

            mock_uvicorn.Config.assert_called_once()
            mock_uvicorn.Server.assert_called_once()
            mock_server.serve.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_no_fastapi(self):
        """Test main function with FastAPI not installed."""
        from models.workers.user_stats.user_stats_worker import main

        mock_worker = MagicMock()
        mock_worker.start = AsyncMock()

        with (
            patch(
                "models.workers.user_stats.user_stats_worker.UserStatsWorker",
                return_value=mock_worker,
            ),
            patch("models.workers.user_stats.user_stats_worker.FastAPI", None),
            patch("models.workers.user_stats.user_stats_worker.logger"),
        ):
            await main()

            mock_worker.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_with_fastapi(self):
        """Test main function with FastAPI installed."""
        from models.workers.user_stats.user_stats_worker import main

        mock_worker = MagicMock()

        with (
            patch(
                "models.workers.user_stats.user_stats_worker.UserStatsWorker",
                return_value=mock_worker,
            ),
            patch("models.workers.user_stats.user_stats_worker.FastAPI"),
            patch("models.workers.user_stats.user_stats_worker.uvicorn"),
            patch(
                "models.workers.user_stats.user_stats_worker.asyncio.gather",
                new_callable=AsyncMock,
            ) as mock_gather,
            patch(
                "models.workers.user_stats.user_stats_worker.run_worker",
                new_callable=AsyncMock,
            ),
            patch(
                "models.workers.user_stats.user_stats_worker.run_server",
                new_callable=AsyncMock,
            ),
            patch("models.workers.user_stats.user_stats_worker.logger"),
        ):
            await main()

            mock_gather.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_with_fastapi_gather_error(self):
        """Test main function handles asyncio.gather error."""
        from models.workers.user_stats.user_stats_worker import main

        mock_worker = MagicMock()

        with (
            patch(
                "models.workers.user_stats.user_stats_worker.UserStatsWorker",
                return_value=mock_worker,
            ),
            patch("models.workers.user_stats.user_stats_worker.FastAPI"),
            patch("models.workers.user_stats.user_stats_worker.uvicorn"),
            patch(
                "models.workers.user_stats.user_stats_worker.asyncio.gather",
                new_callable=AsyncMock,
                side_effect=Exception("Gather error"),
            ),
            patch(
                "models.workers.user_stats.user_stats_worker.run_worker",
                new_callable=AsyncMock,
            ),
            patch(
                "models.workers.user_stats.user_stats_worker.run_server",
                new_callable=AsyncMock,
            ),
            patch("models.workers.user_stats.user_stats_worker.logger"),
            pytest.raises(Exception, match="Gather error"),
        ):
            await main()
