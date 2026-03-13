"""Unit tests for id_generation_worker."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from models.workers.id_generation.id_generation_worker import IdGeneratorWorker
from models.data.rest_api.v1.entitybase.response import WorkerHealthCheckResponse
from models.data.rest_api.v1.entitybase.response.id_response import IdResponse


class TestIdGeneratorWorker:
    """Unit tests for IdGeneratorWorker class."""

    def test_worker_initialization(self):
        """Test worker initialization."""
        worker = IdGeneratorWorker()
        assert worker.worker_id is not None
        assert worker.running is False
        assert worker.enumeration_service is None

    def test_signal_handler_sigterm(self):
        """Test signal handler for SIGTERM."""
        worker = IdGeneratorWorker()
        worker.running = True
        worker._signal_handler(15, None)  # 15 = SIGTERM
        assert worker.running is False

    def test_signal_handler_sigint(self):
        """Test signal handler for SIGINT."""
        worker = IdGeneratorWorker()
        worker.running = True
        worker._signal_handler(2, None)  # 2 = SIGINT
        assert worker.running is False

    def test_health_check_healthy(self):
        """Test health check when worker is healthy."""
        worker = IdGeneratorWorker()
        worker.running = True
        worker.enumeration_service = MagicMock()
        worker.enumeration_service.get_range_status.return_value = MagicMock(
            model_dump=MagicMock(return_value={"ranges": 10})
        )

        response = worker.health_check()

        assert response.status == "healthy"
        assert response.worker_id == worker.worker_id

    def test_health_check_unhealthy(self):
        """Test health check when worker is not running."""
        worker = IdGeneratorWorker()
        worker.running = False
        worker.enumeration_service = None

        response = worker.health_check()

        assert response.status == "unhealthy"

    def test_health_check_exception(self):
        """Test health check when enumeration service throws exception."""
        worker = IdGeneratorWorker()
        worker.running = True
        worker.enumeration_service = MagicMock()
        worker.enumeration_service.get_range_status.side_effect = Exception("Error")

        response = worker.health_check()

        assert response.status == "healthy"
        assert response.range_status == {}

    def test_get_next_id_success(self):
        """Test getting next ID successfully."""
        worker = IdGeneratorWorker()
        mock_service = MagicMock()
        mock_service.get_next_entity_id.return_value = "Q123"
        worker.enumeration_service = mock_service

        response = worker.get_next_id("item")

        assert isinstance(response, IdResponse)
        assert response.id == "Q123"
        mock_service.get_next_entity_id.assert_called_once_with("item")

    def test_get_next_id_service_not_initialized(self):
        """Test getting next ID when service is not initialized."""
        from fastapi import HTTPException

        worker = IdGeneratorWorker()
        worker.enumeration_service = None

        with pytest.raises(HTTPException):
            worker.get_next_id("item")

    @pytest.mark.asyncio
    async def test_shutdown(self):
        """Test worker shutdown."""
        worker = IdGeneratorWorker()
        worker.vitess_client = MagicMock()
        worker.running = True

        await worker._shutdown()

        # Note: _shutdown doesn't set running to False
