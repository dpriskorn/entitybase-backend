import pytest
from unittest.mock import patch, MagicMock

pytestmark = pytest.mark.unit

from models.rest_api.app import app, lifespan


class TestApp:
    def test_app_creation(self) -> None:
        """Test that FastAPI app is created with correct configuration."""
        assert app.title == "Wikibase Backend API"
        assert app.description == "Backend API for Wikibase entity management"
        assert app.version == "1.0.0"
        assert app.router.lifespan_context == lifespan

    @pytest.mark.asyncio
    async def test_lifespan_success(self):
        """Test lifespan context manager with successful client initialization."""
        mock_app = MagicMock()
        mock_clients = MagicMock()
        mock_clients.s3.healthy_connection = True
        mock_clients.vitess.healthy_connection = True

        with (
            patch("models.rest_api.app.Clients", return_value=mock_clients),
            patch("models.rest_api.app.settings") as mock_settings,
        ):
            mock_settings.to_s3_config.return_value = MagicMock()
            mock_settings.to_vitess_config.return_value = MagicMock()
            mock_settings.property_registry_path = "/tmp/registry"

            async with lifespan(mock_app):
                assert mock_app.state.clients == mock_clients

    @pytest.mark.asyncio
    async def test_lifespan_s3_failure(self):
        """Test lifespan with S3 connection failure."""
        mock_app = MagicMock()
        mock_clients = MagicMock()
        mock_clients.s3.healthy_connection = False
        mock_clients.vitess.healthy_connection = True

        with (
            patch("models.rest_api.app.Clients", return_value=mock_clients),
            patch("models.rest_api.app.settings") as mock_settings,
            patch("models.rest_api.app.logger") as mock_logger,
        ):
            mock_settings.to_s3_config.return_value = MagicMock()
            mock_settings.to_vitess_config.return_value = MagicMock()
            mock_settings.property_registry_path = None

            async with lifespan(mock_app):
                mock_logger.warning.assert_called_with("S3 client connection failed")

    @pytest.mark.asyncio
    async def test_lifespan_vitess_failure(self):
        """Test lifespan with Vitess connection failure."""
        mock_app = MagicMock()
        mock_clients = MagicMock()
        mock_clients.s3.healthy_connection = True
        mock_clients.vitess.healthy_connection = False

        with (
            patch("models.rest_api.app.Clients", return_value=mock_clients),
            patch("models.rest_api.app.settings") as mock_settings,
            patch("models.rest_api.app.logger") as mock_logger,
        ):
            mock_settings.to_s3_config.return_value = MagicMock()
            mock_settings.to_vitess_config.return_value = MagicMock()
            mock_settings.property_registry_path = None

            async with lifespan(mock_app):
                mock_logger.warning.assert_called_with(
                    "Vitess client connection failed"
                )

    @pytest.mark.asyncio
    async def test_lifespan_initialization_failure(self):
        """Test lifespan when client initialization fails."""
        mock_app = MagicMock()

        with (
            patch("models.rest_api.app.Clients", side_effect=Exception("Init failed")),
            patch("models.rest_api.app.logger") as mock_logger,
        ):
            with pytest.raises(Exception, match="Init failed"):
                async with lifespan(mock_app):
                    pass

        mock_logger.error.assert_called()
