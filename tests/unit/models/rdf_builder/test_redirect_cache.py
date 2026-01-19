"""Unit tests for redirect cache."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

from models.rdf_builder.redirect_cache import (
    _fetch_entity_redirects_batch,
    load_entity_redirects_batch,
    load_entity_redirects,
)
from models.rest_api.v1.entitybase.response import (
    MetadataLoadResponse,
    RedirectBatchResponse,
)


class TestRedirectCache:
    """Test cases for redirect cache functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.redirects_dir = Path(self.temp_dir)

    def test_load_entity_redirects_batch_success(self) -> None:
        """Test successful batch loading of entity redirects."""
        entity_ids = ["Q1", "Q2", "Q3"]

        mock_response = Mock()
        mock_response.json.return_value = {
            "query": {
                "pages": {
                    "1": {
                        "title": "Q1",
                        "redirects": [{"title": "Q10"}, {"title": "Q11"}],
                    },
                    "2": {
                        "title": "Q2"
                        # No redirects
                    },
                    "3": {"title": "Q3", "redirects": [{"title": "Q30"}]},
                }
            }
        }

        with patch("models.rdf_builder.redirect_cache.requests.get") as mock_get:
            mock_get.return_value = mock_response

            result = load_entity_redirects_batch(entity_ids, self.redirects_dir)

        # Verify response structure
        assert isinstance(result, MetadataLoadResponse)
        assert len(result.results) == 3
        assert all(result.results[entity_id] for entity_id in entity_ids)

        # Verify files were created
        for entity_id in entity_ids:
            file_path = self.redirects_dir / f"{entity_id}.json"
            assert file_path.exists()

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                assert data["id"] == entity_id
                assert "redirects" in data

    def test_load_entity_redirects_batch_empty_list(self) -> None:
        """Test batch loading with empty entity list."""
        result = load_entity_redirects_batch([], self.redirects_dir)

        assert isinstance(result, MetadataLoadResponse)
        assert len(result.results) == 0

    def test_load_entity_redirects_batch_api_error(self) -> None:
        """Test batch loading when API request fails."""
        entity_ids = ["Q1", "Q2"]

        with patch("models.rdf_builder.redirect_cache.requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("API Error")

            result = load_entity_redirects_batch(entity_ids, self.redirects_dir)

        # Should still create empty redirect files for all entities
        assert isinstance(result, MetadataLoadResponse)
        assert len(result.results) == 2
        assert all(result.results[entity_id] for entity_id in entity_ids)

        # Verify files exist with empty redirects
        for entity_id in entity_ids:
            file_path = self.redirects_dir / f"{entity_id}.json"
            assert file_path.exists()

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                assert data["redirects"] == []

    def test_load_entity_redirects_batch_http_error(self) -> None:
        """Test batch loading when HTTP error occurs."""
        entity_ids = ["Q1"]

        with patch("models.rdf_builder.redirect_cache.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.HTTPError(
                "404 Not Found"
            )
            mock_get.return_value = mock_response

            result = load_entity_redirects_batch(entity_ids, self.redirects_dir)

        assert isinstance(result, MetadataLoadResponse)
        assert len(result.results) == 1
        assert result.results["Q1"] is True

    def test_load_entity_redirects_batch_large_list(self) -> None:
        """Test batch loading with more than 50 entities (tests batching)."""
        # Create 75 entity IDs to test batching logic
        entity_ids = [f"Q{i}" for i in range(1, 76)]

        mock_response = Mock()
        mock_response.json.return_value = {
            "query": {
                "pages": {
                    str(i): {
                        "title": f"Q{i}",
                        "redirects": [{"title": f"Q{i}0"}] if i % 2 == 0 else [],
                    }
                    for i in range(1, 76)
                }
            }
        }

        with patch("models.rdf_builder.redirect_cache.requests.get") as mock_get:
            mock_get.return_value = mock_response

            result = load_entity_redirects_batch(entity_ids, self.redirects_dir)

        # Should make 2 API calls (50 + 25)
        assert mock_get.call_count == 2

        assert isinstance(result, MetadataLoadResponse)
        assert len(result.results) == 75

        # Verify all files were created
        for entity_id in entity_ids:
            file_path = self.redirects_dir / f"{entity_id}.json"
            assert file_path.exists()

    @patch("models.rdf_builder.redirect_cache.time.sleep")
    @patch("models.rdf_builder.redirect_cache.requests.get")
    def test_fetch_entity_redirects_batch_success(self, mock_get, mock_sleep) -> None:
        """Test internal _fetch_entity_redirects_batch function."""
        entity_ids = ["Q1", "Q2"]

        mock_response = Mock()
        mock_response.json.return_value = {
            "query": {
                "pages": {
                    "1": {"title": "Q1", "redirects": [{"title": "Q10"}]},
                    "2": {"title": "Q2"},  # No redirects
                }
            }
        }
        mock_get.return_value = mock_response

        result = _fetch_entity_redirects_batch(entity_ids)

        assert isinstance(result, RedirectBatchResponse)
        assert len(result.redirects) == 2
        assert result.redirects["Q1"] == ["Q10"]
        assert result.redirects["Q2"] == []

        # Verify API call parameters
        mock_get.assert_called_once_with(
            "https://www.wikidata.org/w/api.php",
            params={
                "action": "query",
                "prop": "redirects",
                "titles": "Q1|Q2",
                "rdlimit": "max",
                "format": "json",
            },
            timeout=60,
            headers={
                "User-Agent": "WikibaseBackend/1.0 (research@wikibase-backend.org)"
            },
        )

    def test_fetch_entity_redirects_batch_empty_list(self) -> None:
        """Test _fetch_entity_redirects_batch with empty list."""
        result = _fetch_entity_redirects_batch([])

        assert isinstance(result, RedirectBatchResponse)
        assert len(result.redirects) == 0

    @patch("models.rdf_builder.redirect_cache.logger")
    @patch("models.rdf_builder.redirect_cache.time.sleep")
    @patch("models.rdf_builder.redirect_cache.requests.get")
    def test_fetch_entity_redirects_batch_exception(
        self, mock_get, mock_sleep, mock_logger
    ):
        """Test _fetch_entity_redirects_batch handles exceptions."""
        entity_ids = ["Q1", "Q2"]

        mock_get.side_effect = requests.RequestException("Network error")

        result = _fetch_entity_redirects_batch(entity_ids)

        # Should return empty redirects for all entities
        assert isinstance(result, RedirectBatchResponse)
        assert len(result.redirects) == 2
        assert result.redirects["Q1"] == []
        assert result.redirects["Q2"] == []

        # Should log error
        mock_logger.error.assert_called_once()
        assert "Failed to fetch batch 1" in mock_logger.error.call_args[0][0]

    def test_load_entity_redirects_success(self) -> None:
        """Test loading redirects from existing file."""
        entity_id = "Q1"
        test_data = {"id": entity_id, "redirects": ["Q10", "Q11", "Q12"]}

        # Create test file
        file_path = self.redirects_dir / f"{entity_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        result = load_entity_redirects(entity_id, self.redirects_dir)

        assert result == ["Q10", "Q11", "Q12"]

    def test_load_entity_redirects_file_not_found(self) -> None:
        """Test loading redirects when file doesn't exist."""
        with pytest.raises(FileNotFoundError) as exc_info:
            load_entity_redirects("Q999", self.redirects_dir)

        assert "Redirect data for Q999 not found" in str(exc_info.value)

    def test_load_entity_redirects_empty_file(self) -> None:
        """Test loading redirects from empty/malformed file."""
        entity_id = "Q1"
        file_path = self.redirects_dir / f"{entity_id}.json"

        # Create empty file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({}, f)

        result = load_entity_redirects(entity_id, self.redirects_dir)

        assert result == []

    def test_load_entity_redirects_missing_redirects_key(self) -> None:
        """Test loading redirects when redirects key is missing."""
        entity_id = "Q1"
        test_data = {
            "id": entity_id
            # Missing "redirects" key
        }

        file_path = self.redirects_dir / f"{entity_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        result = load_entity_redirects(entity_id, self.redirects_dir)

        assert result == []

    def test_load_entity_redirects_invalid_json(self) -> None:
        """Test loading redirects from invalid JSON file."""
        entity_id = "Q1"
        file_path = self.redirects_dir / f"{entity_id}.json"

        # Create invalid JSON file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("invalid json content")

        with pytest.raises(json.JSONDecodeError):
            load_entity_redirects(entity_id, self.redirects_dir)

    @patch("models.rdf_builder.redirect_cache.logger")
    def test_load_entity_redirects_batch_directory_creation(self, mock_logger) -> None:
        """Test that directories are created when needed."""
        non_existent_dir = self.redirects_dir / "subdir" / "nested"
        entity_ids = ["Q1"]

        mock_response = Mock()
        mock_response.json.return_value = {"query": {"pages": {"1": {"title": "Q1"}}}}

        with patch("models.rdf_builder.redirect_cache.requests.get") as mock_get:
            mock_get.return_value = mock_response

            result = load_entity_redirects_batch(entity_ids, non_existent_dir)

        assert isinstance(result, MetadataLoadResponse)
        assert non_existent_dir.exists()
        assert (non_existent_dir / "Q1.json").exists()

    @patch("models.rdf_builder.redirect_cache.time.sleep")
    @patch("models.rdf_builder.redirect_cache.requests.get")
    def test_api_call_parameters(self, mock_get, mock_sleep) -> None:
        """Test that API is called with correct parameters."""
        entity_ids = ["Q1", "Q2", "Q3"]

        mock_response = Mock()
        mock_response.json.return_value = {"query": {"pages": {}}}
        mock_get.return_value = mock_response

        _fetch_entity_redirects_batch(entity_ids)

        # Verify the API call
        call_args = mock_get.call_args
        assert call_args[1]["timeout"] == 60
        assert (
            call_args[1]["headers"]["User-Agent"]
            == "WikibaseBackend/1.0 (research@wikibase-backend.org)"
        )
        assert call_args[1]["params"]["titles"] == "Q1|Q2|Q3"
        assert call_args[1]["params"]["rdlimit"] == "max"

    def test_unicode_handling(self) -> None:
        """Test that Unicode characters are handled correctly."""
        entity_id = "Q1"
        test_data = {"id": entity_id, "redirects": ["Q_Résumé", "Q_Москва", "Q_北京"]}

        file_path = self.redirects_dir / f"{entity_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(test_data, f, ensure_ascii=False)

        result = load_entity_redirects(entity_id, self.redirects_dir)

        assert result == ["Q_Résumé", "Q_Москва", "Q_北京"]
