"""Unit tests for models.rest_api.app module."""

import logging
import pytest
from unittest.mock import AsyncMock, PropertyMock, patch, MagicMock

from fastapi import FastAPI


class TestRestApiApp:
    """Unit tests for models.rest_api.app module."""

    def test_app_initialization(self):
        """Test that the FastAPI app is initialized correctly."""
        from models.rest_api.app import app

        assert app is not None
        assert app.title == "Wikibase Backend API"
        assert app.description == "Backend API for Wikibase entity management"
        assert app.version == "v2026.4.8"

    def test_app_has_lifespan(self):
        """Test that app has lifespan configured."""
        from models.rest_api.app import app

        assert app.router.lifespan_context is not None

    def test_logging_configuration(self):
        """Test that logging is configured at module level."""
        from models.rest_api import app as app_module

        # Check that logger is accessible
        logger = app_module.logger
        assert logger is not None
        assert logger.name == "models.rest_api.app"

    def test_log_level_import(self):
        """Test that log_level is imported."""
        from models.rest_api.app import log_level

        assert log_level is not None

    @pytest.mark.asyncio
    async def test_lifespan_startup_success(self, mocker):
        """Test that lifespan startup initializes StateHandler correctly."""
        from models.rest_api.app import lifespan

        app_mock = FastAPI()
        mock_state_handler = MagicMock()
        mock_state_handler.start.return_value = None

        mocker.patch(
            "models.rest_api.app.StateHandler",
            return_value=mock_state_handler,
        )

        async with lifespan(app_mock) as _:
            assert hasattr(app_mock.state, "state_handler")
            mock_state_handler.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_startup_failure(self, mocker):
        """Test that lifespan startup failure raises exception."""
        from models.rest_api.app import lifespan

        app_mock = FastAPI()
        mock_state_handler = MagicMock()
        mock_state_handler.start.side_effect = RuntimeError("Startup failed")

        mocker.patch(
            "models.rest_api.app.StateHandler",
            return_value=mock_state_handler,
        )

        with pytest.raises(RuntimeError) as exc_info:
            async with lifespan(app_mock) as _:
                pass

        assert "Startup failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_lifespan_shutdown_logs(self, mocker, caplog):
        """Test that lifespan shutdown logs messages."""
        from models.rest_api.app import lifespan

        app_mock = FastAPI()
        mock_state_handler = MagicMock()
        mock_state_handler.start.return_value = None
        mock_state_handler.async_shutdown = AsyncMock()

        mocker.patch(
            "models.rest_api.app.StateHandler",
            return_value=mock_state_handler,
        )

        with caplog.at_level(logging.DEBUG):
            async with lifespan(app_mock) as _:
                pass

        assert "Shutting down" in caplog.text

    def test_settings_import(self):
        """Test that settings are imported."""
        from models.rest_api.app import settings

        assert settings is not None

    def test_state_handler_import(self):
        """Test that StateHandler is imported."""
        from models.rest_api.app import StateHandler

        assert StateHandler is not None
