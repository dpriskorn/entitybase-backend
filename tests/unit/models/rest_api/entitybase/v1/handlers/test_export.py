"""Unit tests for export.py."""

from unittest.mock import MagicMock, patch
import pytest

from models.infrastructure.s3.exceptions import S3NotFoundError
from models.rest_api.entitybase.v1.handlers.export import ExportHandler


class TestExportHandler:
    """Tests for ExportHandler methods."""

    @pytest.fixture
    def mock_state(self) -> MagicMock:
        state = MagicMock()
        state.mysql_client.entity_exists.return_value = True
        state.mysql_client.get_head.return_value = 5
        state.s3_client.read_revision.return_value = MagicMock(
            revision={"labels": {}, "descriptions": {}}
        )
        state.property_registry = MagicMock()
        return state

    @pytest.fixture
    def handler(self, mock_state: MagicMock) -> ExportHandler:
        return ExportHandler(state=mock_state)

    def test_get_entity_data_turtle_mysql_not_initialized(self) -> None:
        mock_state = MagicMock()
        mock_state.mysql_client = None
        handler = ExportHandler(state=mock_state)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            handler.get_entity_data_turtle("Q42")
        assert exc_info.value.status_code == 503

    def test_get_entity_data_turtle_entity_not_found(self) -> None:
        mock_state = MagicMock()
        mock_state.mysql_client.entity_exists.return_value = False
        handler = ExportHandler(state=mock_state)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            handler.get_entity_data_turtle("Q42")
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail

    def test_get_entity_data_turtle_no_revisions(self) -> None:
        mock_state = MagicMock()
        mock_state.mysql_client.entity_exists.return_value = True
        mock_state.mysql_client.get_head.return_value = 0
        handler = ExportHandler(state=mock_state)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            handler.get_entity_data_turtle("Q42")
        assert exc_info.value.status_code == 404
        assert "no revisions" in exc_info.value.detail

    def test_get_entity_data_turtle_s3_not_found(
        self, handler: ExportHandler, mock_state: MagicMock
    ) -> None:
        mock_state.s3_client.read_revision.side_effect = S3NotFoundError("Not found")

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            handler.get_entity_data_turtle("Q42")
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail

    def test_get_entity_data_turtle_success(
        self, handler: ExportHandler, mock_state: MagicMock
    ) -> None:
        from models.rest_api.entitybase.v1.services.rdf_service import (
            serialize_entity_to_turtle,
        )

        mock_state.s3_client.read_revision.return_value = MagicMock(
            revision={
                "labels": {"en": "test"},
                "descriptions": {},
                "aliases": {},
                "claims": [],
            }
        )

        with patch(
            "models.rest_api.entitybase.v1.handlers.export.serialize_entity_to_turtle",
            return_value="<turtle>data</turtle>",
        ):
            result = handler.get_entity_data_turtle("Q42")

        assert result.turtle == "<turtle>data</turtle>"
        mock_state.mysql_client.entity_exists.assert_called_once_with("Q42")
        mock_state.mysql_client.get_head.assert_called_once_with("Q42")
