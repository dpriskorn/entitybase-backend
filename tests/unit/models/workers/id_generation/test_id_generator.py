"""Tests for ID generation worker."""

from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError

from models.workers.id_generation.id_generator import IdGeneratorWorker, IdResponse


class TestIdResponse:
    """Test the IdResponse model."""

    def test_valid_id_response(self) -> None:
        """Test creating a valid IdResponse."""
        response = IdResponse(id="Q123")
        assert response.id == "Q123"

    def test_id_response_validation(self) -> None:
        """Test IdResponse validates input."""
        # Should accept string IDs
        response = IdResponse(id="P456")
        assert response.id == "P456"

        # Should work with any string
        response = IdResponse(id="L789")
        assert response.id == "L789"

    def test_id_response_serialization(self) -> None:
        """Test IdResponse can be serialized to dict."""
        response = IdResponse(id="Q123")
        data = response.model_dump()
        assert data == {"id": "Q123"}


class TestIdGeneratorWorker:
    """Test the IdGeneratorWorker class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.worker = IdGeneratorWorker()

    def test_worker_initialization(self) -> None:
        """Test worker initializes correctly."""
        assert self.worker.worker_id.startswith("worker-")
        assert self.worker.running is False
        assert self.worker.enumeration_service is None

    def test_worker_with_custom_id(self) -> None:
        """Test worker with custom worker ID."""
        worker = IdGeneratorWorker(worker_id="test-worker")
        assert worker.worker_id == "test-worker"

    @patch("models.workers.id_generation.id_generator.EnumerationService")
    def test_get_next_id_success(self, mock_enumeration_service_class: Mock) -> None:
        """Test get_next_id returns IdResponse on success."""
        # Setup mock
        mock_service = Mock()
        mock_service.get_next_entity_id.return_value = "Q123"
        mock_enumeration_service_class.return_value = mock_service

        self.worker.enumeration_service = mock_service

        # Call method
        result = self.worker.get_next_id("item")

        # Verify result
        assert isinstance(result, IdResponse)
        assert result.id == "Q123"
        mock_service.get_next_entity_id.assert_called_once_with("item")

    def test_get_next_id_not_initialized(self) -> None:
        """Test get_next_id raises error when worker not initialized."""
        with pytest.raises(ValidationError) as exc_info:
            self.worker.get_next_id("item")

        assert "Worker not initialized" in str(exc_info.value)

    def test_health_check_not_running(self) -> None:
        """Test health check when worker is not running."""
        health = self.worker.health_check()
        assert health.status == "unhealthy"
        assert health.worker_id == self.worker.worker_id
        assert health.range_status == {}

    @patch("models.workers.id_generation.id_generator.EnumerationService")
    def test_health_check_running(self, mock_enumeration_service_class: Mock) -> None:
        """Test health check when worker is running."""
        # Setup mock
        mock_service = Mock()
        mock_service.get_range_status.return_value = {"Q": {"current": 100, "max": 200}}
        mock_enumeration_service_class.return_value = mock_service

        self.worker.enumeration_service = mock_service
        self.worker.running = True

        # Call health check
        health = self.worker.health_check()

        # Verify
        assert health.status == "healthy"
        assert health.worker_id == self.worker.worker_id
        assert health.range_status == {"Q": {"current": 100, "max": 200}}
