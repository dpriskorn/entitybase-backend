import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.unit

from models.rest_api.entitybase.handlers.entity.wikidata_import import (
    EntityJsonImportHandler,
)
from models.rest_api.entitybase.request import EntityJsonImportRequest
from models.rest_api.entitybase.response import EntityJsonImportResponse
from models.services.wikidata_import_service import WikidataImportService


class TestEntityJsonImportHandler:
    """Unit tests for EntityJsonImportHandler."""

    @pytest.fixture
    def mock_clients(self) -> tuple[MagicMock, MagicMock, AsyncMock, MagicMock]:
        """Create mock clients for testing."""
        vitess_client = MagicMock()
        s3_client = MagicMock()
        stream_producer = AsyncMock()
        validator = MagicMock()
        return vitess_client, s3_client, stream_producer, validator

    @pytest.fixture
    def sample_entity_json(self) -> dict[str, Any]:
        """Sample Wikidata entity JSON."""
        return {
            "type": "item",
            "id": "Q123",
            "labels": {"en": {"language": "en", "value": "Test Item"}},
            "descriptions": {"en": {"language": "en", "value": "A test item"}},
            "aliases": {"en": [{"language": "en", "value": "Test"}]},
            "claims": {
                "P31": [
                    {
                        "mainsnak": {
                            "property": "P31",
                            "datavalue": {"value": {"id": "Q5"}},
                        }
                    }
                ]
            },
        }

    def test_process_entity_line_valid(
        self, sample_entity_json: dict[str, Any]
    ) -> None:
        """Test processing a valid entity line."""
        line = json.dumps(sample_entity_json) + ","

        with tempfile.TemporaryDirectory() as temp_dir:
            error_log_path = Path(temp_dir) / "errors.log"
            result = EntityJsonImportHandler._process_entity_line(
                line, 1, error_log_path
            )

            assert result == sample_entity_json
            assert not error_log_path.exists()

    def test_process_entity_line_malformed(self) -> None:
        """Test processing a malformed JSON line."""
        line = '{"type": "item", "id": "Q123", invalid}'

        with tempfile.TemporaryDirectory() as temp_dir:
            error_log_path = Path(temp_dir) / "errors.log"
            result = EntityJsonImportHandler._process_entity_line(
                line, 1, error_log_path
            )

            assert result is None
            assert error_log_path.exists()

            with open(error_log_path, "r") as f:
                log_content = f.read()
                assert "ERROR: Failed to parse line 1" in log_content
                assert "invalid}" in log_content

    def test_process_entity_line_empty(self) -> None:
        """Test processing an empty line."""
        line = ""

        with tempfile.TemporaryDirectory() as temp_dir:
            error_log_path = Path(temp_dir) / "errors.log"
            result = EntityJsonImportHandler._process_entity_line(
                line, 1, error_log_path
            )

            assert result is None
            assert not error_log_path.exists()

    def test_check_entity_exists_true(
        self, mock_clients: tuple[MagicMock, MagicMock, AsyncMock, MagicMock]
    ) -> None:
        """Test entity existence check when entity exists."""
        _, s3_client, _, _ = mock_clients

        # Mock S3 client to not raise exception (entity exists)
        s3_client.read_revision = MagicMock()

        result = EntityJsonImportHandler._check_entity_exists("Q123", s3_client)
        assert result is True

    def test_check_entity_exists_false(
        self, mock_clients: tuple[MagicMock, MagicMock, AsyncMock, MagicMock]
    ) -> None:
        """Test entity existence check when entity doesn't exist."""
        _, s3_client, _, _ = mock_clients

        # Mock S3 client to raise exception (entity doesn't exist)
        s3_client.read_revision = MagicMock(side_effect=Exception("Not found"))

        result = EntityJsonImportHandler._check_entity_exists("Q123", s3_client)
        assert result is False

    @patch(
        "models.services.wikidata_import_service.WikidataImportService.transform_to_create_request"
    )
    @pytest.mark.asyncio
    async def test_import_entities_from_jsonl_success(
        self,
        mock_transform: MagicMock,
        mock_clients: tuple[MagicMock, MagicMock, AsyncMock, MagicMock],
        sample_entity_json: dict[str, Any],
    ) -> None:
        """Test successful import of entities from JSONL file."""
        vitess_client, s3_client, stream_producer, validator = mock_clients

        # Create temporary JSONL file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(json.dumps(sample_entity_json) + ",\n")
            jsonl_path = f.name

        try:
            # Mock dependencies
            mock_transform.return_value = MagicMock()
            vitess_client.create_entity = AsyncMock()
            vitess_client.entity_exists.return_value = False
            vitess_client.entity_repository.get_entity.return_value = None
            s3_client.read_revision = MagicMock(
                side_effect=Exception("Not found")
            )  # Entity doesn't exist

            request = EntityJsonImportRequest(
                jsonl_file_path=jsonl_path,
                start_line=1,  # Override default to include line 1 for test
                worker_id="test-worker",
            )

            result = await EntityJsonImportHandler.import_entities_from_jsonl(
                request, vitess_client, s3_client, stream_producer, validator
            )

            assert isinstance(result, EntityJsonImportResponse)
            assert result.processed_count == 1
            assert result.imported_count == 1
            assert result.failed_count == 0
            assert "test-worker" in result.error_log_path

        finally:
            Path(jsonl_path).unlink()


class TestWikidataImportService:
    """Unit tests for WikidataImportService."""

    @patch("models.services.wikidata_import_service.requests.get")
    def test_fetch_entity_data_success(self, mock_get: MagicMock) -> None:
        """Test successful entity data fetching."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "entities": {
                "Q123": {
                    "type": "item",
                    "id": "Q123",
                    "labels": {"en": {"language": "en", "value": "Test"}},
                }
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = WikidataImportService.fetch_entity_data("Q123")

        assert result.data["type"] == "item"
        assert result.data["id"] == "Q123"
        mock_get.assert_called_once()

    @patch("models.services.wikidata_import_service.requests.get")
    def test_fetch_entity_data_not_found(self, mock_get: MagicMock) -> None:
        """Test fetching non-existent entity."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"entities": {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Entity Q123 not found"):
            WikidataImportService.fetch_entity_data("Q123")

    @pytest.fixture
    def sample_entity_json(self) -> dict[str, Any]:
        return {
            "id": "Q12346",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Test Item"}},
            "descriptions": {},
            "aliases": {},
            "claims": {},
            "sitelinks": {},
        }

    def test_transform_to_create_request(
        self, sample_entity_json: dict[str, Any]
    ) -> None:
        """Test transformation of Wikidata JSON to EntityCreateRequest."""
        result = WikidataImportService.transform_to_create_request(sample_entity_json)

        assert result.id == "Q12346"
        assert result.type == "item"
        assert "en" in result.labels
        assert len(result.descriptions) == 0
        assert len(result.aliases) == 0
        assert "P31" in result.claims
        assert result.edit_type.value == "BOT_IMPORT"
