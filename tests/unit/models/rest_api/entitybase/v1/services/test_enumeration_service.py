"""Unit tests for enumeration_service."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from models.rest_api.entitybase.v1.services.enumeration_service import EnumerationService


class TestEnumerationService:
    """Unit tests for EnumerationService."""

    def test_get_next_entity_id_item(self):
        """Test getting next entity ID for item type."""
        mock_vitess_client = MagicMock()
        mock_range_manager = MagicMock()
        mock_range_manager.get_next_id.return_value = "Q300000001"

        with patch.object(
            EnumerationService,
            "model_post_init",
            lambda self, ctx: setattr(self, "range_manager", mock_range_manager),
        ):
            service = EnumerationService(
                worker_id="test-worker",
                vitess_client=mock_vitess_client,
            )

            result = service.get_next_entity_id("item")

            assert result == "Q300000001"
            mock_range_manager.get_next_id.assert_called_once_with("Q")

    def test_get_next_entity_id_property(self):
        """Test getting next entity ID for property type."""
        mock_vitess_client = MagicMock()
        mock_range_manager = MagicMock()
        mock_range_manager.get_next_id.return_value = "P30001"

        with patch.object(
            EnumerationService,
            "model_post_init",
            lambda self, ctx: setattr(self, "range_manager", mock_range_manager),
        ):
            service = EnumerationService(
                worker_id="test-worker",
                vitess_client=mock_vitess_client,
            )

            result = service.get_next_entity_id("property")

            assert result == "P30001"
            mock_range_manager.get_next_id.assert_called_once_with("P")

    def test_get_next_entity_id_lexeme(self):
        """Test getting next entity ID for lexeme type."""
        mock_vitess_client = MagicMock()
        mock_range_manager = MagicMock()
        mock_range_manager.get_next_id.return_value = "L5000001"

        with patch.object(
            EnumerationService,
            "model_post_init",
            lambda self, ctx: setattr(self, "range_manager", mock_range_manager),
        ):
            service = EnumerationService(
                worker_id="test-worker",
                vitess_client=mock_vitess_client,
            )

            result = service.get_next_entity_id("lexeme")

            assert result == "L5000001"
            mock_range_manager.get_next_id.assert_called_once_with("L")

    def test_get_next_entity_id_entityschema(self):
        """Test getting next entity ID for entityschema type."""
        mock_vitess_client = MagicMock()
        mock_range_manager = MagicMock()
        mock_range_manager.get_next_id.return_value = "E50001"

        with patch.object(
            EnumerationService,
            "model_post_init",
            lambda self, ctx: setattr(self, "range_manager", mock_range_manager),
        ):
            service = EnumerationService(
                worker_id="test-worker",
                vitess_client=mock_vitess_client,
            )

            result = service.get_next_entity_id("entityschema")

            assert result == "E50001"
            mock_range_manager.get_next_id.assert_called_once_with("E")

    def test_get_next_entity_id_invalid_type(self):
        """Test getting next entity ID with invalid type raises error."""
        mock_vitess_client = MagicMock()
        mock_range_manager = MagicMock()

        with patch.object(
            EnumerationService,
            "model_post_init",
            lambda self, ctx: setattr(self, "range_manager", mock_range_manager),
        ):
            service = EnumerationService(
                worker_id="test-worker",
                vitess_client=mock_vitess_client,
            )

            with pytest.raises(HTTPException) as exc_info:
                service.get_next_entity_id("invalid_type")

            assert exc_info.value.status_code == 400
            assert "Unsupported entity type" in str(exc_info.value.detail)

    def test_get_range_status(self):
        """Test getting range status."""
        mock_vitess_client = MagicMock()
        mock_range_manager = MagicMock()
        mock_status = MagicMock()
        mock_range_manager.get_range_status.return_value = mock_status

        with patch.object(
            EnumerationService,
            "model_post_init",
            lambda self, ctx: setattr(self, "range_manager", mock_range_manager),
        ):
            service = EnumerationService(
                worker_id="test-worker",
                vitess_client=mock_vitess_client,
            )

            result = service.get_range_status()

            assert result == mock_status
            mock_range_manager.get_range_status.assert_called_once()

    def test_confirm_id_usage_valid(self):
        """Test confirming valid ID usage."""
        with patch("models.rest_api.entitybase.v1.services.enumeration_service.logger") as mock_logger:
            EnumerationService.confirm_id_usage("Q300000001")

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "Confirmed usage of ID Q300000001" in call_args

    def test_confirm_id_usage_invalid_format(self):
        """Test confirming ID with invalid format."""
        with patch("models.rest_api.entitybase.v1.services.enumeration_service.logger") as mock_logger:
            EnumerationService.confirm_id_usage("invalid")

            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args[0][0]
            assert "Invalid entity ID format" in call_args

    def test_confirm_id_usage_non_numeric(self):
        """Test confirming ID with non-numeric part."""
        with patch("models.rest_api.entitybase.v1.services.enumeration_service.logger") as mock_logger:
            EnumerationService.confirm_id_usage("Qabc")

            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args[0][0]
            assert "Invalid entity ID format" in call_args

    def test_confirm_id_usage_empty_raises_index_error(self):
        """Test confirming empty ID raises IndexError (code bug - empty string access)."""
        with pytest.raises(IndexError):
            EnumerationService.confirm_id_usage("")

    def test_model_post_init_initializes_range_manager(self):
        """Test that model_post_init properly initializes range manager."""
        mock_vitess_client = MagicMock()
        mock_id_range_manager_class = MagicMock()

        with patch(
            "models.rest_api.entitybase.v1.services.enumeration_service.IdRangeManager",
            mock_id_range_manager_class,
        ) as mock_id_range_manager:
            service = EnumerationService(
                worker_id="test-worker",
                vitess_client=mock_vitess_client,
            )

            mock_id_range_manager.assert_called_once()
            call_kwargs = mock_id_range_manager.call_args[1]
            assert call_kwargs["vitess_client"] == mock_vitess_client
            assert "Q" in call_kwargs["min_ids"]
            assert "P" in call_kwargs["min_ids"]
            assert "L" in call_kwargs["min_ids"]
            assert "E" in call_kwargs["min_ids"]

    def test_model_post_init_database_init_failure_is_handled(self):
        """Test that database initialization failure is handled gracefully."""
        mock_vitess_client = MagicMock()
        mock_id_range_manager_class = MagicMock()
        mock_range_manager_instance = MagicMock()
        mock_id_range_manager_class.return_value = mock_range_manager_instance
        mock_range_manager_instance.initialize_from_database.side_effect = Exception(
            "DB connection failed"
        )

        with patch(
            "models.rest_api.entitybase.v1.services.enumeration_service.IdRangeManager",
            mock_id_range_manager_class,
        ), patch(
            "models.rest_api.entitybase.v1.services.enumeration_service.logger"
        ) as mock_logger:
            service = EnumerationService(
                worker_id="test-worker",
                vitess_client=mock_vitess_client,
            )

            mock_logger.warning.assert_called()
            call_args = mock_logger.warning.call_args[0][0]
            assert "Failed to initialize ID ranges from database" in call_args
