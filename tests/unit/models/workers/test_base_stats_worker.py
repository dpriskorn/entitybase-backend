"""Unit tests for base_stats_worker."""

from types import SimpleNamespace
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from models.workers.base_stats_worker import BaseStatsWorker
from models.workers.utils import calculate_seconds_until_next_run


class ConcreteStatsWorker(BaseStatsWorker):
    """Concrete implementation for testing BaseStatsWorker."""

    async def run_daily_computation(self) -> None:
        pass

    def get_enabled_setting(self) -> bool:
        return True

    def get_schedule_setting(self) -> str:
        return "0 2"


class TestBaseStatsWorker:
    """Unit tests for BaseStatsWorker."""

    def test_state_property_with_client(self):
        """Test state property returns SimpleNamespace with mysql_client."""
        with patch("models.workers.base_stats_worker.BaseStatsWorker.model_post_init"):
            worker = ConcreteStatsWorker.model_construct(db_client="test-client")

        result = worker.state

        assert isinstance(result, SimpleNamespace)
        assert result.mysql_client == "test-client"

    def test_state_property_without_client(self):
        """Test state property with None mysql_client."""
        with patch("models.workers.base_stats_worker.BaseStatsWorker.model_post_init"):
            worker = ConcreteStatsWorker()

        result = worker.state

        assert result.mysql_client is None

    @pytest.mark.asyncio
    async def test_stop(self):
        """Test stop sets running to False."""
        with patch("models.workers.base_stats_worker.BaseStatsWorker.model_post_init"):
            worker = ConcreteStatsWorker(running=True)

        await worker.stop()

        assert worker.running is False

    @pytest.mark.asyncio
    async def test_start_disabled(self):
        """Test start returns early when disabled."""
        with (
            patch.object(
                ConcreteStatsWorker, "get_enabled_setting", return_value=False
            ),
            patch("models.workers.mysql_worker.MysqlClient"),
            patch("models.workers.mysql_worker.settings"),
        ):
            worker = ConcreteStatsWorker()

            with patch(
                "models.workers.base_stats_worker.calculate_seconds_until_next_run"
            ) as mock_calc:
                await worker.start()

                mock_calc.assert_not_called()

    @pytest.mark.asyncio
    async def test_health_check_healthy(self):
        """Test health_check returns healthy when running."""
        with patch("models.workers.base_stats_worker.BaseStatsWorker.model_post_init"):
            worker = ConcreteStatsWorker(running=True)

        result = await worker.health_check()

        assert result.status == "healthy"
        assert result.worker_id == worker.worker_id

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self):
        """Test health_check returns unhealthy when not running."""
        with patch("models.workers.base_stats_worker.BaseStatsWorker.model_post_init"):
            worker = ConcreteStatsWorker(running=False)

        result = await worker.health_check()

        assert result.status == "unhealthy"

    @pytest.mark.asyncio
    async def test_health_check_last_run_none(self):
        """Test health_check shows last_run as None."""
        with patch("models.workers.base_stats_worker.BaseStatsWorker.model_post_init"):
            worker = ConcreteStatsWorker(running=True)

        result = await worker.health_check()

        assert result.details["last_run"] is None

    @pytest.mark.asyncio
    async def test_health_check_last_run_set(self):
        """Test health_check shows last_run isoformat."""
        from datetime import datetime

        with patch("models.workers.base_stats_worker.BaseStatsWorker.model_post_init"):
            worker = ConcreteStatsWorker(running=True)

        worker.last_run = datetime(2024, 1, 1, 12, 0, 0)

        result = await worker.health_check()

        assert result.details["last_run"] == "2024-01-01T12:00:00"

    @pytest.mark.asyncio
    async def test_start_loop_one_iteration(self):
        """Test start loop runs one full iteration."""
        worker = ConcreteStatsWorker()

        with (
            patch.object(
                ConcreteStatsWorker, "run_daily_computation", new_callable=AsyncMock
            ) as mock_computation,
            patch(
                "models.workers.base_stats_worker.calculate_seconds_until_next_run",
                return_value=0,
            ),
            patch(
                "models.workers.base_stats_worker.asyncio.sleep", new_callable=AsyncMock
            ) as mock_sleep,
            patch("models.workers.mysql_worker.MysqlClient"),
            patch("models.workers.mysql_worker.settings"),
        ):

            async def stop_after_sleep(*args, **kwargs):
                worker.running = False

            mock_sleep.side_effect = stop_after_sleep

            await worker.start()

            mock_computation.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_loop_exception_recovery(self):
        """Test start loop recovers from exceptions."""
        worker = ConcreteStatsWorker()

        with (
            patch.object(
                ConcreteStatsWorker, "run_daily_computation", new_callable=AsyncMock
            ) as mock_computation,
            patch(
                "models.workers.base_stats_worker.calculate_seconds_until_next_run",
                return_value=0,
            ),
            patch(
                "models.workers.base_stats_worker.asyncio.sleep", new_callable=AsyncMock
            ) as mock_sleep,
            patch("models.workers.mysql_worker.MysqlClient"),
            patch("models.workers.mysql_worker.settings"),
        ):
            mock_computation.side_effect = [Exception("Computation error"), None]

            call_count = 0

            async def stop_after_two_calls(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count >= 2:
                    worker.running = False

            mock_sleep.side_effect = stop_after_two_calls

            await worker.start()

            assert mock_computation.call_count >= 1
