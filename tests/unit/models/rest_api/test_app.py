"""Tests for models.rest_api.app module."""

import pytest
import logging


class TestFastAPIApp:
    """Test suite for the FastAPI app initialization and configuration."""

    def test_app_initialization(self):
        """Test that the FastAPI app is initialized correctly."""
        from models.rest_api.app import app

        assert app is not None
        assert app.title == "Wikibase Backend API"
        assert app.version == "1.0.0"
        assert len(app.description) > 0

    def test_app_has_lifespan_configured(self):
        """Test that app has lifespan configured."""
        from models.rest_api.app import app

        assert app.router.lifespan_context is not None

    def test_logging_configuration(self):
        """Test that logging is configured at module level."""
        from models.rest_api.app import logger

        assert logger is not None
        assert logger.name == "models.rest_api.app"

    @pytest.mark.asyncio
    async def test_lifespan_startup_success(self, mocker):
        """Test that lifespan startup initializes StateHandler correctly."""
        from models.rest_api.app import lifespan
        from fastapi import FastAPI

        app_mock = FastAPI()
        mock_state_handler = mocker.Mock()
        mock_state_handler.start.return_value = None

        mocker.patch(
            "models.rest_api.app.StateHandler",
            return_value=mock_state_handler
        )

        async with lifespan(app_mock) as _:
            assert hasattr(app_mock.state, "state_handler")
            assert app_mock.state.state_handler == mock_state_handler
            mock_state_handler.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_shutdown_logs_message(self, mocker, caplog):
        """Test that lifespan shutdown logs appropriate messages."""
        from models.rest_api.app import lifespan
        from fastapi import FastAPI

        app_mock = FastAPI()
        mock_state_handler = mocker.Mock()
        mock_state_handler.start.return_value = None

        mocker.patch(
            "models.rest_api.app.StateHandler",
            return_value=mock_state_handler
        )

        with caplog.at_level(logging.DEBUG):
            async with lifespan(app_mock) as _:
                pass

        assert "Shutting down..." in caplog.text

    @pytest.mark.asyncio
    async def test_lifespan_startup_failure(self, mocker):
        """Test that lifespan startup failure raises exception."""
        from models.rest_api.app import lifespan
        from fastapi import FastAPI

        app_mock = FastAPI()
        mock_state_handler = mocker.Mock()
        mock_state_handler.start.side_effect = RuntimeError("Startup failed")

        mocker.patch(
            "models.rest_api.app.StateHandler",
            return_value=mock_state_handler
        )

        with pytest.raises(RuntimeError) as exc_info:
            async with lifespan(app_mock) as _:
                pass

        assert "Startup failed" in str(exc_info.value)

    def test_settings_import(self):
        """Test that settings are imported and accessible."""
        from models.rest_api.app import settings

        assert settings is not None
        assert hasattr(settings, "log_level")

    def test_state_handler_import(self):
        """Test that StateHandler is imported."""
        from models.rest_api.app import StateHandler

        assert StateHandler is not None
