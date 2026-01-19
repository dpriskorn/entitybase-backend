import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, "src")

from models.workers.backlink_statistics.backlink_statistics_worker import (
    BacklinkStatisticsWorker,
)


class TestBacklinkStatisticsWorkerIntegration:
    """Integration tests for BacklinkStatisticsWorker with mocked dependencies"""

    @pytest.fixture
    def mock_vitess_client(self) -> MagicMock:
        """Mock Vitess client with backlink repository"""
        client = MagicMock()
        client.backlink_repository = MagicMock()
        client.connection_manager.get_connection.return_value.__enter__.return_value = (
            MagicMock()
        )
        return client

    @pytest.fixture
    def worker(self, mock_vitess_client: MagicMock) -> BacklinkStatisticsWorker:
        """Create worker instance with mocked client"""
        worker = BacklinkStatisticsWorker()
        worker.vitess_client = mock_vitess_client
        return worker

    @pytest.mark.asyncio
    async def test_full_statistics_workflow_success(
        self, worker: BacklinkStatisticsWorker, mock_vitess_client: MagicMock
    ) -> None:
        """Test complete statistics computation and storage workflow"""
        # Mock the stats computation
        mock_stats = MagicMock()
        mock_stats.total_backlinks = 1500
        mock_stats.unique_entities_with_backlinks = 750
        mock_stats.top_entities_by_backlinks = [
            {"entity_id": "Q42", "backlink_count": 100},
            {"entity_id": "Q43", "backlink_count": 95},
        ]

        with (
            patch(
                "models.workers.backlink_statistics.backlink_statistics_worker.BacklinkStatisticsService"
            ) as mock_service_class,
            patch(
                "models.workers.backlink_statistics.backlink_statistics_worker.date"
            ) as mock_date,
        ):
            mock_service = mock_service_class.return_value
            mock_service.compute_daily_stats.return_value = mock_stats
            mock_date.today.return_value.isoformat.return_value = "2024-01-13"

            # Run the computation
            await worker.run_daily_computation()

            # Verify service was called correctly
            mock_service.compute_daily_stats.assert_called_once_with(mock_vitess_client)

            # Verify repository method was called with correct parameters
            mock_vitess_client.backlink_repository.insert_backlink_statistics.assert_called_once_with(
                conn=mock_vitess_client.connection_manager.get_connection.return_value.__enter__.return_value,
                date="2024-01-13",
                total_backlinks=1500,
                unique_entities_with_backlinks=750,
                top_entities_by_backlinks=mock_stats.top_entities_by_backlinks,
            )

            # Verify connection commit was called
            mock_conn = mock_vitess_client.connection_manager.get_connection.return_value.__enter__.return_value
            mock_conn.commit.assert_called_once()

            # Verify last_run was set
            assert worker.last_run is not None

    @pytest.mark.asyncio
    async def test_statistics_computation_failure(
        self, worker: BacklinkStatisticsWorker, mock_vitess_client: MagicMock
    ) -> None:
        """Test handling of statistics computation failure"""
        with patch(
            "models.workers.backlink_statistics.backlink_statistics_worker.BacklinkStatisticsService"
        ) as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.compute_daily_stats.side_effect = Exception(
                "Computation failed"
            )

            # Should raise the exception
            with pytest.raises(Exception) as exc_info:
                await worker.run_daily_computation()

            assert "Computation failed" in str(exc_info.value)

            # Repository should not be called
            mock_vitess_client.backlink_repository.insert_backlink_statistics.assert_not_called()

    @pytest.mark.asyncio
    async def test_statistics_storage_failure(
        self, worker: BacklinkStatisticsWorker, mock_vitess_client: MagicMock
    ) -> None:
        """Test handling of statistics storage failure"""
        # Mock successful computation
        mock_stats = MagicMock()
        mock_stats.total_backlinks = 100
        mock_stats.unique_entities_with_backlinks = 50
        mock_stats.top_entities_by_backlinks = []

        # Mock repository failure
        mock_vitess_client.backlink_repository.insert_backlink_statistics.side_effect = Exception(
            "Storage failed"
        )

        with (
            patch(
                "models.workers.backlink_statistics.backlink_statistics_worker.BacklinkStatisticsService"
            ) as mock_service_class,
            patch(
                "models.workers.backlink_statistics.backlink_statistics_worker.date"
            ) as mock_date,
        ):
            mock_service = mock_service_class.return_value
            mock_service.compute_daily_stats.return_value = mock_stats
            mock_date.today.return_value.isoformat.return_value = "2024-01-13"

            # Should raise the storage exception
            with pytest.raises(Exception) as exc_info:
                await worker.run_daily_computation()

            assert "Storage failed" in str(exc_info.value)

            # Verify repository was called
            mock_vitess_client.backlink_repository.insert_backlink_statistics.assert_called_once()

    @pytest.mark.asyncio
    async def test_worker_without_vitess_client(
        self, worker: BacklinkStatisticsWorker
    ) -> None:
        """Test behavior when vitess client is not available"""
        worker.vitess_client = None

        # Should not crash, just skip
        await worker.run_daily_computation()

        # Verify last_run was not set
        assert worker.last_run is None

    @pytest.mark.asyncio
    async def test_worker_schedule_parsing(
        self, worker: BacklinkStatisticsWorker
    ) -> None:
        """Test that worker correctly parses backlink_stats_schedule"""
        with (
            patch(
                "models.workers.backlink_statistics.backlink_statistics_worker.settings"
            ) as mock_settings,
            patch(
                "models.workers.backlink_statistics.backlink_statistics_worker.datetime"
            ) as mock_datetime,
            patch(
                "models.workers.backlink_statistics.backlink_statistics_worker.timedelta"
            ) as mock_timedelta,
        ):
            # Mock current time as 10:00 AM
            mock_now = MagicMock()
            mock_now.time.return_value = MagicMock()
            mock_now.time.return_value.__lt__ = MagicMock(
                return_value=True
            )  # Before target time
            mock_datetime.utcnow.return_value = mock_now

            # Mock target time calculation
            mock_target = MagicMock()
            mock_datetime.combine.return_value = mock_target

            # Mock time difference
            mock_timedelta.return_value = MagicMock()
            mock_target.__sub__ = MagicMock(return_value=MagicMock())
            mock_target.__sub__.return_value.total_seconds.return_value = (
                7200  # 2 hours
            )

            mock_settings.backlink_stats_schedule = "0 12 * * *"  # 12:00 PM

            seconds = worker._calculate_seconds_until_next_run()

            assert seconds == 7200  # 2 hours until 12 PM

    @pytest.mark.asyncio
    async def test_worker_health_check(self, worker: BacklinkStatisticsWorker) -> None:
        """Test worker health check functionality"""
        worker.running = True
        worker.last_run = MagicMock()
        worker.last_run.isoformat.return_value = "2024-01-13T10:00:00"

        health = await worker.health_check()

        assert health.status == "healthy"
        assert health.worker_id == worker.worker_id
        assert health.details["running"] is True
        assert health.details["last_run"] == "2024-01-13T10:00:00"

    @pytest.mark.asyncio
    async def test_worker_health_check_not_running(
        self, worker: BacklinkStatisticsWorker
    ) -> None:
        """Test worker health check when not running"""
        worker.running = False
        worker.last_run = None

        health = await worker.health_check()

        assert health.status == "unhealthy"
        assert health.details["running"] is False
        assert health.details["last_run"] is None
