"""Tests for models.services.wikidata_import_service module."""

import pytest
import requests
from models.services.wikidata_import_service import WikidataImportService
from models.data.raw_entity import RawEntityData


class TestWikidataImportServiceFetchEntityData:
    """Test suite for the fetch_entity_data method."""

    def test_fetch_entity_data_success(self, mocker):
        """Test successful entity fetch from Wikidata API."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "entities": {
                "Q42": {
                    "id": "Q42",
                    "type": "item",
                    "labels": {"en": {"language": "en", "value": "Douglas Adams"}},
                }
            }
        }
        mock_response.raise_for_status.return_value = None

        mocker.patch("requests.get", return_value=mock_response)

        result = WikidataImportService.fetch_entity_data("Q42")

        assert isinstance(result, RawEntityData)
        assert result.data["id"] == "Q42"
        assert result.data["type"] == "item"

    def test_fetch_entity_data_api_error(self, mocker):
        """Test API error handling in fetch_entity_data."""
        mock_response = mocker.Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}

        mocker.patch("requests.get", return_value=mock_response)

        with pytest.raises(ValueError) as exc_info:
            WikidataImportService.fetch_entity_data("Q42")

        assert "Wikidata API error" in str(exc_info.value)

    def test_fetch_entity_data_missing_entity(self, mocker):
        """Test handling when entity is not found in response."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"entities": {}}
        mock_response.raise_for_status.return_value = None

        mocker.patch("requests.get", return_value=mock_response)

        with pytest.raises(ValueError) as exc_info:
            WikidataImportService.fetch_entity_data("Q42")

        assert "not found in Wikidata" in str(exc_info.value)

    def test_fetch_entity_data_deleted_entity(self, mocker):
        """Test handling when entity is marked as missing/deleted."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "entities": {
                "Q42": {
                    "id": "Q42",
                    "type": "item",
                    "missing": "",
                }
            }
        }
        mock_response.raise_for_status.return_value = None

        mocker.patch("requests.get", return_value=mock_response)

        with pytest.raises(ValueError) as exc_info:
            WikidataImportService.fetch_entity_data("Q42")

        assert "is missing/deleted" in str(exc_info.value)

    def test_fetch_entity_data_request_exception(self, mocker):
        """Test handling of request exceptions."""
        mocker.patch(
            "requests.get", side_effect=requests.RequestException("Network error")
        )

        with pytest.raises(ValueError) as exc_info:
            WikidataImportService.fetch_entity_data("Q42")

        assert "Failed to fetch" in str(exc_info.value)
        assert "Network error" in str(exc_info.value)


class TestWikidataImportServiceTransformToCreateRequest:
    """Test suite for the transform_to_create_request method."""

    def test_transform_to_create_request_item(self):
        """Test transforming Wikidata item data to EntityCreateRequest."""
        wikidata_data = {
            "id": "Q42",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Test Item"}},
            "descriptions": {"en": {"language": "en", "value": "Test Description"}},
            "aliases": {"en": [{"language": "en", "value": "Test Alias"}]},
            "claims": {"P31": [{"mainsnak": {"datavalue": {"value": "Q5"}}}]},
            "sitelinks": {"enwiki": {"site": "enwiki", "title": "Test Title"}},
        }

        result = WikidataImportService.transform_to_create_request(wikidata_data)

        assert result.id == "Q42"
        assert result.type == "item"
        assert "en" in result.labels
        assert "en" in result.descriptions
        assert result.edit_type.value == "bot-import"

    def test_transform_to_create_request_property(self):
        """Test transforming Wikidata property data to EntityCreateRequest."""
        wikidata_data = {
            "id": "P31",
            "type": "property",
            "labels": {"en": {"language": "en", "value": "instance of"}},
            "descriptions": {},
            "aliases": {},
            "claims": {},
        }

        result = WikidataImportService.transform_to_create_request(wikidata_data)

        assert result.id == "P31"
        assert result.type == "property"

    def test_transform_to_create_request_lexeme(self):
        """Test transforming Wikidata lexeme data to EntityCreateRequest."""
        wikidata_data = {
            "id": "L123",
            "type": "lexeme",
            "labels": {"en": {"language": "en", "value": "test"}},
            "descriptions": {},
            "aliases": {},
            "claims": {},
        }

        result = WikidataImportService.transform_to_create_request(wikidata_data)

        assert result.id == "L123"
        assert result.type == "lexeme"

    def test_transform_to_create_request_unknown_type(self):
        """Test transforming Wikidata data with unknown type."""
        wikidata_data = {
            "id": "X123",
            "type": "unknown",
            "labels": {},
            "descriptions": {},
            "aliases": {},
            "claims": {},
        }

        result = WikidataImportService.transform_to_create_request(wikidata_data)

        assert result.type == "unknown"

    def test_transform_to_create_request_empty_fields(self):
        """Test transforming Wikidata data with empty fields."""
        wikidata_data = {
            "id": "Q999",
            "type": "item",
            "labels": {},
            "descriptions": {},
            "aliases": {},
            "claims": {},
            "sitelinks": {},
        }

        result = WikidataImportService.transform_to_create_request(wikidata_data)

        assert result.id == "Q999"
        assert result.type == "item"
        assert result.labels == {}
        assert result.descriptions == {}
        assert result.aliases == {}
        assert result.claims == {}
        assert result.sitelinks == {}


class TestWikidataImportServiceImportEntity:
    """Test suite for the import_entity method."""

    def test_import_entity_end_to_end(self, mocker):
        """Test complete entity import process with mocked requests."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "entities": {
                "Q42": {
                    "id": "Q42",
                    "type": "item",
                    "labels": {"en": {"language": "en", "value": "Test"}},
                    "descriptions": {},
                    "aliases": {},
                    "claims": {},
                }
            }
        }
        mock_response.raise_for_status.return_value = None

        mocker.patch("requests.get", return_value=mock_response)

        result = WikidataImportService.import_entity("Q42")

        assert result.id == "Q42"
        assert result.type == "item"
        assert result.edit_type.value == "bot-import"

    def test_import_entity_fetch_failure(self, mocker):
        """Test import_entity when fetch fails."""
        mocker.patch(
            "requests.get", side_effect=requests.RequestException("Network error")
        )

        with pytest.raises(ValueError) as exc_info:
            WikidataImportService.import_entity("Q42")

        assert "Failed to fetch" in str(exc_info.value)
