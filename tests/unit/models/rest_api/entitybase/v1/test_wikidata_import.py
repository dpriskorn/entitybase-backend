import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = pytest.mark.unit

from models.data.rest_api.v1.entitybase.request import EntityJsonImportRequest
from models.data.rest_api.v1.entitybase.response import EntityJsonImportResponse
from models.rest_api.entitybase.v1.handlers.entity.wikidata_import import (
    EntityJsonImportHandler,
)
from models.services.wikidata_import_service import WikidataImportService


class TestEntityJsonImportHandler:
    """Unit tests for EntityJsonImportHandler."""

    def setup_method(self):
        """Set up test fixtures."""
        from unittest.mock import MagicMock

        self.state = MagicMock()

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
        assert result.edit_type.value == "bot-import"
