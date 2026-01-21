import json
from unittest.mock import patch, MagicMock

import pytest

pytestmark = pytest.mark.unit

from models.rdf_builder.entity_cache import (
    fetch_entity_metadata_batch,
    load_entity_metadata_batch,
    load_entity_metadata,
)


class TestFetchEntityMetadataBatch:
    def test_fetch_empty_list(self) -> None:
        """Test fetching with empty entity list."""
        result = fetch_entity_metadata_batch([])
        assert result.metadata == {}

    @patch("models.rdf_builder.entity_cache.requests.post")
    def test_fetch_single_entity_success(self, mock_post) -> None:
        """Test fetching metadata for single entity."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": {
                "bindings": [
                    {
                        "entity": {"value": "http://www.wikidata.org/entity/Q42"},
                        "label": {"value": "Douglas Adams"},
                        "description": {"value": "English writer and humorist"},
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = fetch_entity_metadata_batch(["Q42"])

        assert "Q42" in result.metadata
        metadata = result.metadata["Q42"]
        assert metadata.id == "Q42"
        assert metadata.labels["en"].value == "Douglas Adams"
        assert metadata.descriptions["en"].value == "English writer and humorist"

    @patch("models.rdf_builder.entity_cache.requests.post")
    def test_fetch_multiple_entities_batch(self, mock_post) -> None:
        """Test fetching metadata in batches."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": {
                "bindings": [
                    {
                        "entity": {"value": "http://www.wikidata.org/entity/Q1"},
                        "label": {"value": "universe"},
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # 101 entities to trigger batching
        entity_ids = [f"Q{i}" for i in range(101)]
        result = fetch_entity_metadata_batch(entity_ids)

        # Should have made 2 requests (100 + 1)
        assert mock_post.call_count == 2

    @patch("models.rdf_builder.entity_cache.requests.post")
    def test_fetch_request_failure(self, mock_post) -> None:
        """Test handling of request failure."""
        mock_post.side_effect = Exception("Network error")

        result = fetch_entity_metadata_batch(["Q42"])

        assert result.metadata["Q42"] is None


class TestLoadEntityMetadataBatch:
    @patch("models.rdf_builder.entity_cache.fetch_entity_metadata_batch")
    def test_load_batch_success(self, mock_fetch, tmp_path) -> None:
        """Test loading and saving metadata batch successfully."""
        mock_fetch.return_value.metadata = {
            "Q42": MagicMock(
                model_dump=lambda: {"id": "Q42", "labels": {"en": {"value": "test"}}}
            )
        }

        result = load_entity_metadata_batch(["Q42"], tmp_path)

        assert result.results["Q42"] is True
        json_file = tmp_path / "Q42.json"
        assert json_file.exists()
        data = json.loads(json_file.read_text())
        assert data["id"] == "Q42"

    @patch("models.rdf_builder.entity_cache.fetch_entity_metadata_batch")
    def test_load_batch_failure(self, mock_fetch, tmp_path) -> None:
        """Test loading batch with fetch failure."""
        mock_fetch.return_value.metadata = {"Q42": None}

        result = load_entity_metadata_batch(["Q42"], tmp_path)

        assert result.results["Q42"] is False
        json_file = tmp_path / "Q42.json"
        assert not json_file.exists()


class TestLoadEntityMetadata:
    def test_load_existing_metadata(self, tmp_path) -> None:
        """Test loading existing metadata file."""
        data = {"id": "Q42", "labels": {"en": {"language": "en", "value": "test"}}}
        json_file = tmp_path / "Q42.json"
        json_file.write_text(json.dumps(data))

        result = load_entity_metadata("Q42", tmp_path)

        assert result.id == "Q42"
        assert result.labels["en"].value == "test"

    def test_load_nonexistent_metadata(self, tmp_path) -> None:
        """Test loading nonexistent metadata raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Entity Q42 not found"):
            load_entity_metadata("Q42", tmp_path)

    def test_load_corrupted_metadata(self, tmp_path) -> None:
        """Test loading corrupted JSON metadata."""
        json_file = tmp_path / "Q42.json"
        json_file.write_text("invalid json")

        with pytest.raises(Exception):  # json.JSONDecodeError
            load_entity_metadata("Q42", tmp_path)

    @patch("models.rdf_builder.entity_cache.fetch_entity_metadata_batch")
    def test_load_batch_serialization_error(self, mock_fetch, tmp_path) -> None:
        """Test loading batch with serialization error."""
        mock_fetch.return_value.metadata = {
            "Q42": MagicMock(
                model_dump=lambda: {"id": "Q42", "labels": {"en": {"value": "test"}}}
            )
        }

        # Mock json.dump to raise exception
        with patch(
            "models.rdf_builder.entity_cache.json.dump",
            side_effect=Exception("Serialization error"),
        ):
            result = load_entity_metadata_batch(["Q42"], tmp_path)

        assert result.results["Q42"] is False
        json_file = tmp_path / "Q42.json"
        assert not json_file.exists()

    def test_cache_hit_scenario(self, tmp_path) -> None:
        """Test cache hit when metadata file exists and is valid."""
        data = {"id": "Q42", "labels": {"en": {"language": "en", "value": "test"}}}
        json_file = tmp_path / "Q42.json"
        json_file.write_text(json.dumps(data))

        result = load_entity_metadata("Q42", tmp_path)

        assert result.id == "Q42"
        assert result.labels["en"].value == "test"

    def test_cache_miss_scenario(self, tmp_path) -> None:
        """Test cache miss when metadata file does not exist."""
        with pytest.raises(FileNotFoundError, match="Entity Q42 not found"):
            load_entity_metadata("Q42", tmp_path)
