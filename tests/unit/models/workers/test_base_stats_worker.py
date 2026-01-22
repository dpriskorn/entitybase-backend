"""Unit tests for base_stats_worker."""

import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone

from models.workers.base_stats_worker import BaseStatsWorker


class TestStatsWorker(BaseStatsWorker):
    """Test implementation of BaseStatsWorker."""

    def get_enabled_setting(self) -> bool:
        return True

    def get_schedule_setting(self) -> str:
        return "0 2"  # 2 AM daily

    async def run_daily_computation(self) -> None:
        pass


class TestBaseStatsWorker:
    """Unit tests for base_stats_worker."""

    def test_calculate_seconds_until_next_run_same_day(self):
        """Test calculating seconds until next run on same day."""
        worker = TestStatsWorker(vitess_client=MagicMock())

        with patch('models.workers.base_stats_worker.datetime') as mock_datetime:
            now = datetime(2023, 1, 1, 1, 0, 0, tzinfo=timezone.utc)  # 1 AM
            mock_datetime.now.return_value = now
            mock_datetime.combine = datetime.combine

            seconds = worker._calculate_seconds_until_next_run()

            # Should be 1 hour until 2 AM
            assert seconds == 3600

    def test_calculate_seconds_until_next_run_next_day(self):
        """Test calculating seconds until next run on next day."""
        worker = TestStatsWorker(vitess_client=MagicMock())

        with patch('models.workers.base_stats_worker.datetime') as mock_datetime:
            now = datetime(2023, 1, 1, 3, 0, 0, tzinfo=timezone.utc)  # 3 AM, after 2 AM
            mock_datetime.now.return_value = now
            mock_datetime.combine = datetime.combine

            seconds = worker._calculate_seconds_until_next_run()

            # Should be 23 hours until next 2 AM
            assert seconds == 23 * 3600

    def test_calculate_seconds_until_next_run_invalid_schedule(self):
        """Test calculating with invalid schedule falls back to 2 AM."""
        worker = TestStatsWorker(vitess_client=MagicMock())

        with patch.object(worker, 'get_schedule_setting', return_value="invalid"), \
             patch('models.workers.base_stats_worker.datetime') as mock_datetime:

            now = datetime(2023, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = now
            mock_datetime.combine = datetime.combine

            seconds = worker._calculate_seconds_until_next_run()

            assert seconds == 3600  # 1 hour to 2 AM

    @pytest.mark.asyncio
    async def test_start_disabled(self):
        """Test starting disabled worker."""
        worker = TestStatsWorker(vitess_client=MagicMock())

        with patch.object(worker, 'get_enabled_setting', return_value=False), \
             patch('models.workers.base_stats_worker.logger') as mock_logger:

            await worker.start()

            mock_logger.info.assert_called_with("TestStatsWorker disabled")

    @pytest.mark.asyncio
    async def test_start_enabled(self):
        """Test starting enabled worker."""
        worker = TestStatsWorker(vitess_client=MagicMock())

        with patch.object(worker, 'get_enabled_setting', return_value=True), \
             patch('models.workers.base_stats_worker.VitessClient') as mock_vitess_client, \
             patch.object(worker, '_calculate_seconds_until_next_run', return_value=0), \
             patch('models.workers.base_stats_worker.logger') as mock_logger, \
             patch('asyncio.sleep', side_effect=asyncio.CancelledError), \
             patch('models.workers.base_stats_worker.settings') as mock_settings:

            mock_settings.to_vitess_config.return_value = {}

            with pytest.raises(asyncio.CancelledError):
                await worker.start()

            mock_logger.info.assert_any_call(f"Starting TestStatsWorker {worker.worker_id}")
            assert worker.running is True

    @pytest.mark.asyncio
    async def test_start_with_exception(self):
        """Test starting worker with exception in loop."""
        worker = TestStatsWorker(vitess_client=MagicMock())

        with patch.object(worker, 'get_enabled_setting', return_value=True), \
             patch('models.workers.base_stats_worker.VitessClient'), \
             patch.object(worker, '_calculate_seconds_until_next_run', return_value=0), \
             patch.object(worker, 'run_daily_computation', side_effect=Exception("Test error")), \
             patch('models.workers.base_stats_worker.logger') as mock_logger, \
             patch('asyncio.sleep', side_effect=asyncio.CancelledError), \
             patch('models.workers.base_stats_worker.settings'):

            with pytest.raises(asyncio.CancelledError):
                await worker.start()

            mock_logger.error.assert_called_with("Error in worker loop: Test error")

    @pytest.mark.asyncio
    async def test_stop(self):
        """Test stopping worker."""
        worker = TestStatsWorker(vitess_client=MagicMock())
        worker.running = True

        with patch('models.workers.base_stats_worker.logger') as mock_logger:
            await worker.stop()

            assert worker.running is False
            mock_logger.info.assert_called_with(f"Stopping TestStatsWorker {worker.worker_id}")

    def test_health_check_running(self):
        """Test health check when running."""
        worker = TestStatsWorker(vitess_client=MagicMock())
        worker.running = True
        worker.worker_id = "test-123"

        result = asyncio.run(worker.health_check())

        assert result.status == "healthy"
        assert result.worker_id == "test-123"

    def test_health_check_not_running(self):
        """Test health check when not running."""
        worker = TestStatsWorker(vitess_client=MagicMock())
        worker.running = False

        result = asyncio.run(worker.health_check())

        assert result.status == "unhealthy"
