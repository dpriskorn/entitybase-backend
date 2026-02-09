"""Tests for lifespan failure scenarios and state_handler edge cases."""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse


class TestLifespanFailureScenarios:
    """Test lifespan behavior when initialization fails."""

    @pytest.mark.asyncio
    async def test_lifespan_failure_without_state_handler(self):
        """Test that lifespan finally block handles missing state_handler gracefully."""
        from models.rest_api.main import lifespan

        app_mock = FastAPI()
        with patch(
            "models.rest_api.main.StateHandler",
            side_effect=RuntimeError("Failed to initialize"),
        ):
            with pytest.raises(RuntimeError):
                async with lifespan(app_mock):
                    pass

        assert not hasattr(app_mock.state, "state_handler")

    @pytest.mark.asyncio
    async def test_lifespan_failure_in_state_handler_init(self):
        """Test that StateHandler initialization failure doesn't crash finally block."""
        from models.rest_api.main import lifespan

        app_mock = FastAPI()
        with patch("models.rest_api.main.StateHandler") as mock_handler:
            mock_handler.side_effect = ValueError("Configuration error")

            with pytest.raises(ValueError):
                async with lifespan(app_mock):
                    pass

        assert not hasattr(app_mock.state, "state_handler")


class TestStartupMiddleware:
    """Test StartupMiddleware behavior during initialization."""

    @pytest.mark.asyncio
    async def test_middleware_blocks_requests_during_startup(self):
        """Test that middleware returns 503 for API endpoints during startup."""
        from models.rest_api.main import StartupMiddleware

        middleware = StartupMiddleware(app=Mock())
        request = Mock(spec=Request)
        request.url.path = "/api/v1/entities/Q1"
        request.app.state = Mock()

        setattr(request.app.state, "state_handler", None)

        call_next_mock = AsyncMock(return_value=Mock())

        response = await middleware.dispatch(request, call_next_mock)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 503
        assert call_next_mock.call_count == 0

    @pytest.mark.asyncio
    async def test_middleware_allows_health_endpoint_during_startup(self):
        """Test that health endpoint is always accessible."""
        from models.rest_api.main import StartupMiddleware

        middleware = StartupMiddleware(app=Mock())
        request = Mock(spec=Request)
        request.url.path = "/health"
        request.app.state = Mock()

        setattr(request.app.state, "state_handler", None)

        mock_response = Mock()
        call_next_mock = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(request, call_next_mock)

        assert response == mock_response
        assert call_next_mock.call_count == 1

    @pytest.mark.asyncio
    async def test_middleware_allows_requests_after_startup(self):
        """Test that middleware allows requests once state_handler is initialized."""
        from models.rest_api.main import StartupMiddleware

        middleware = StartupMiddleware(app=Mock())
        request = Mock(spec=Request)
        request.url.path = "/api/v1/entities/Q1"
        request.app.state = Mock()

        mock_state_handler = Mock()
        setattr(request.app.state, "state_handler", mock_state_handler)

        mock_response = Mock()
        call_next_mock = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(request, call_next_mock)

        assert response == mock_response
        assert call_next_mock.call_count == 1

    @pytest.mark.asyncio
    async def test_middleware_allows_docs_endpoint_during_startup(self):
        """Test that docs endpoint is always accessible."""
        from models.rest_api.main import StartupMiddleware

        middleware = StartupMiddleware(app=Mock())
        request = Mock(spec=Request)
        request.url.path = "/docs"
        request.app.state = Mock()

        setattr(request.app.state, "state_handler", None)

        mock_response = Mock()
        call_next_mock = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(request, call_next_mock)

        assert response == mock_response
        assert call_next_mock.call_count == 1

    @pytest.mark.asyncio
    async def test_middleware_handles_missing_state_handler_attribute(self):
        """Test that middleware handles missing attribute gracefully."""
        from models.rest_api.main import StartupMiddleware

        middleware = StartupMiddleware(app=Mock())
        request = Mock(spec=Request)
        request.url.path = "/api/v1/entities/Q1"

        class MockState:
            """Mock state that raises AttributeError for missing attributes."""

            def __getattr__(self, name):
                raise AttributeError(
                    f"'{type(self).__name__}' object has no attribute '{name}'"
                )

        request.app.state = MockState()

        mock_response = Mock()
        call_next_mock = AsyncMock(return_value=mock_response)

        response = await middleware.dispatch(request, call_next_mock)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 503
        assert call_next_mock.call_count == 0


class TestHealthCheckWithStateHandler:
    """Test health check endpoint with various state_handler states."""

    def test_health_check_without_state_handler(self, api_client):
        """Test health check returns 503 when state_handler is not set."""
        from models.rest_api.main import app

        app.state.__dict__.pop("state_handler", None)

        response = api_client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "starting"
        assert data["s3"] == "disconnected"
        assert data["vitess"] == "disconnected"

    def test_health_check_with_none_state_handler(self, api_client):
        """Test health check returns 503 when state_handler is None."""
        from models.rest_api.main import app

        app.state.state_handler = None

        response = api_client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "starting"

    def test_health_check_returns_timestamp(self, api_client):
        """Test health check always returns timestamp."""
        from models.rest_api.main import app
        from datetime import datetime

        app.state.__dict__.pop("state_handler", None)

        response = api_client.get("/health")

        data = response.json()
        assert "timestamp" in data

        iso_timestamp = data["timestamp"]
        datetime.fromisoformat(iso_timestamp)
