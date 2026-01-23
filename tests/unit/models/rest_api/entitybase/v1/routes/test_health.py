"""Unit tests for health routes."""

from unittest.mock import MagicMock, patch

from models.data.rest_api.v1.response import HealthCheckResponse
from models.rest_api.entitybase.v1.routes.health import health_check_endpoint


class TestHealthRoutes:
    """Unit tests for health routes."""

    def test_health_check_endpoint_success(self) -> None:
        """Test successful health check endpoint."""
        # Mock response
        mock_response = MagicMock()

        # Mock the health_check function
        mock_health_response = HealthCheckResponse(
            status="ok",
            s3="connected",
            vitess="connected",
            timestamp="2023-12-25T12:00:00+00:00"
        )

        with patch("models.rest_api.entitybase.v1.routes.health.health_check", return_value=mock_health_response):
            # Call the endpoint
            result = health_check_endpoint(mock_response)

            # Verify result
            assert isinstance(result, HealthCheckResponse)
            assert result.status == "ok"
            assert result.s3 == "connected"
            assert result.vitess == "connected"
            assert "timestamp" in result.model_fields

    def test_health_check_endpoint_unhealthy(self) -> None:
        """Test health check endpoint when services are unhealthy."""
        # Mock response
        mock_response = MagicMock()

        # Mock the health_check function with unhealthy status
        mock_health_response = HealthCheckResponse(
            status="ok",
            s3="disconnected",
            vitess="disconnected",
            timestamp="2023-12-25T12:00:00+00:00"
        )

        with patch("models.rest_api.entitybase.v1.routes.health.health_check", return_value=mock_health_response):
            # Call the endpoint
            result = health_check_endpoint(mock_response)

            # Verify result
            assert result.status == "ok"
            assert result.s3 == "disconnected"
            assert result.vitess == "disconnected"