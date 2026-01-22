"""Unit tests for health routes."""

from unittest.mock import MagicMock

from models.rest_api.entitybase.v1.response import HealthCheckResponse
from models.rest_api.entitybase.v1.routes.health import health_check_endpoint


class TestHealthRoutes:
    """Unit tests for health routes."""

    def test_health_check_endpoint_success(self) -> None:
        """Test successful health check endpoint."""
        # Mock response
        mock_response = MagicMock()

        # Mock the health_check function
        mock_health_response = HealthCheckResponse(
            status="healthy",
            s3="healthy",
            vitess="healthy"
        )

        with unittest.mock.patch("models.rest_api.entitybase.v1.routes.health.health_check", return_value=mock_health_response):
            # Call the endpoint
            result = health_check_endpoint(mock_response)

            # Verify result
            assert isinstance(result, HealthCheckResponse)
            assert result.status == "healthy"
            assert result.version == "1.0.0"
            assert "database" in result.services
            assert "s3" in result.services

    def test_health_check_endpoint_unhealthy(self) -> None:
        """Test health check endpoint when services are unhealthy."""
        # Mock response
        mock_response = MagicMock()

        # Mock the health_check function with unhealthy status
        mock_health_response = HealthCheckResponse(
            status="unhealthy",
            s3="healthy",
            vitess="unhealthy"
        )

        with unittest.mock.patch("models.rest_api.entitybase.v1.routes.health.health_check", return_value=mock_health_response):
            # Call the endpoint
            result = health_check_endpoint(mock_response)

            # Verify result
            assert result.status == "unhealthy"
            assert result.services["database"] == "unhealthy"
            assert result.services["s3"] == "healthy"