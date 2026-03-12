"""Unit tests for health response models."""

import pytest

from models.data.rest_api.v1.entitybase.response.health import (
    HealthCheckResponse,
    HealthResponse,
    WorkerHealthCheckResponse,
)


class TestHealthResponse:
    """Unit tests for HealthResponse model."""

    def test_basic_instantiation(self):
        """Test basic instantiation."""
        response = HealthResponse(status="healthy")
        assert response.status == "healthy"

    def test_model_dump(self):
        """Test model_dump()."""
        response = HealthResponse(status="unhealthy")
        dumped = response.model_dump()
        assert dumped == {"status": "unhealthy"}


class TestHealthCheckResponse:
    """Unit tests for HealthCheckResponse model."""

    def test_basic_instantiation(self):
        """Test basic instantiation."""
        response = HealthCheckResponse(
            status="healthy",
            s3="healthy",
            vitess="healthy",
            timestamp="2024-01-01T00:00:00Z",
        )
        assert response.status == "healthy"
        assert response.s3 == "healthy"
        assert response.vitess == "healthy"

    def test_model_dump(self):
        """Test model_dump()."""
        response = HealthCheckResponse(
            status="healthy",
            s3="healthy",
            vitess="unhealthy",
            timestamp="2024-01-01T00:00:00Z",
        )
        dumped = response.model_dump()
        assert dumped["s3"] == "healthy"
        assert dumped["vitess"] == "unhealthy"


class TestWorkerHealthCheckResponse:
    """Unit tests for WorkerHealthCheckResponse model."""

    def test_basic_instantiation(self):
        """Test basic instantiation."""
        response = WorkerHealthCheckResponse(
            status="healthy",
            worker_id="worker-001",
        )
        assert response.status == "healthy"
        assert response.worker_id == "worker-001"

    def test_with_details(self):
        """Test with details."""
        response = WorkerHealthCheckResponse(
            status="healthy",
            worker_id="worker-001",
            details={"running": True, "last_run": "2024-01-01T00:00:00Z"},
        )
        assert response.details["running"] is True

    def test_with_range_status(self):
        """Test with range_status."""
        response = WorkerHealthCheckResponse(
            status="healthy",
            worker_id="worker-001",
            range_status={"min_id": 1000, "max_id": 2000},
        )
        assert response.range_status["min_id"] == 1000

    def test_default_details(self):
        """Test default details is empty dict."""
        response = WorkerHealthCheckResponse(
            status="healthy",
            worker_id="worker-001",
        )
        assert response.details == {}

    def test_default_range_status(self):
        """Test default range_status is empty dict."""
        response = WorkerHealthCheckResponse(
            status="healthy",
            worker_id="worker-001",
        )
        assert response.range_status == {}
