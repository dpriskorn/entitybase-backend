"""Unit tests for StateHandler in state.py."""

from unittest.mock import MagicMock, patch
import pytest

from models.rest_api.entitybase.v1.handlers.state import StateHandler


class TestStateHandlerStreamingBackend:
    """Tests for _is_streaming_backend_healthy."""

    def test_streaming_backend_healthy_redpanda_success(self) -> None:
        mock_settings = MagicMock()
        mock_settings.streaming_backend = "redpanda"
        handler = StateHandler.model_construct(settings=mock_settings)

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("requests.get", return_value=mock_response) as mock_get:
            result = handler._is_streaming_backend_healthy()

        assert result is True
        mock_get.assert_called_once_with("http://redpanda-health:8080", timeout=5)

    def test_streaming_backend_healthy_redpanda_failure(self) -> None:
        mock_settings = MagicMock()
        mock_settings.streaming_backend = "redpanda"
        handler = StateHandler.model_construct(settings=mock_settings)

        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch("requests.get", return_value=mock_response) as mock_get:
            result = handler._is_streaming_backend_healthy()

        assert result is False

    def test_streaming_backend_healthy_redpanda_exception(self) -> None:
        mock_settings = MagicMock()
        mock_settings.streaming_backend = "redpanda"
        handler = StateHandler.model_construct(settings=mock_settings)

        with patch("requests.get", side_effect=Exception("Connection refused")):
            result = handler._is_streaming_backend_healthy()

        assert result is False

    def test_streaming_backend_healthy_unknown_backend(self) -> None:
        mock_settings = MagicMock()
        mock_settings.streaming_backend = "unknown"
        handler = StateHandler.model_construct(settings=mock_settings)

        result = handler._is_streaming_backend_healthy()

        assert result is False


class TestStateHandlerProperties:
    """Tests for StateHandler config properties."""

    def test_entity_diff_stream_config(self) -> None:
        mock_settings = MagicMock()
        mock_settings.get_entity_diff_stream_config = "diff_config"
        handler = StateHandler.model_construct(settings=mock_settings)

        assert handler.entity_diff_stream_config == "diff_config"

    def test_entity_change_stream_config(self) -> None:
        mock_settings = MagicMock()
        mock_settings.get_entity_change_stream_config = "change_config"
        handler = StateHandler.model_construct(settings=mock_settings)

        assert handler.entity_change_stream_config == "change_config"

    def test_user_change_stream_config(self) -> None:
        mock_settings = MagicMock()
        mock_settings.get_user_change_stream_config = "user_config"
        handler = StateHandler.model_construct(settings=mock_settings)

        assert handler.user_change_stream_config == "user_config"

    def test_s3_config(self) -> None:
        mock_settings = MagicMock()
        mock_settings.get_s3_config = "s3_config"
        handler = StateHandler.model_construct(settings=mock_settings)

        assert handler.s3_config == "s3_config"

    def test_mysql_config(self) -> None:
        mock_settings = MagicMock()
        mock_settings.get_mysql_config = "mysql_config"
        handler = StateHandler.model_construct(settings=mock_settings)

        assert handler.mysql_config == "mysql_config"
