"""Unit tests for batch routes."""

import unittest
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from models.rest_api.entitybase.routes.batch import (
    get_batch_sitelinks,
    get_batch_labels,
    get_batch_descriptions,
    get_batch_aliases,
    get_batch_statements,
)


class TestBatchRoutes:
    """Unit tests for batch route functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_request = Mock()
        self.mock_clients = Mock()
        self.mock_request.app.state.clients = self.mock_clients
        self.mock_s3 = Mock()
        self.mock_clients.s3 = self.mock_s3
        self.mock_vitess = Mock()
        self.mock_clients.vitess = self.mock_vitess

    @patch("models.rest_api.entitybase.routes.batch.EntityReadHandler")
    async def test_get_batch_statements_success(self, mock_handler_class):
        """Test successful batch statements retrieval."""
        mock_handler = Mock()
        mock_handler.get_entity.return_value = Mock(
            entity_data={"statements": {"P31": []}}
        )
        mock_handler_class.return_value = mock_handler

        result = await get_batch_statements(self.mock_request, "Q42")

        assert result["Q42"] == {"P31": []}
        mock_handler.get_entity.assert_called_once()

    async def test_get_batch_statements_request_none(self):
        """Test get_batch_statements raises error when request is None."""
        with pytest.raises(HTTPException) as exc_info:
            await get_batch_statements(None, "Q42")
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Request not provided"

    async def test_get_batch_statements_too_many_entities(self):
        """Test get_batch_statements raises error for too many entities."""
        entity_ids = ",".join([f"Q{i}" for i in range(21)])
        with pytest.raises(HTTPException) as exc_info:
            await get_batch_statements(self.mock_request, entity_ids)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Too many entities (max 20)"

    @patch("models.rest_api.entitybase.routes.batch.EntityReadHandler")
    async def test_get_batch_statements_with_properties(self, mock_handler_class):
        """Test batch statements with property filtering."""
        mock_handler = Mock()
        mock_handler.get_entity.return_value = Mock(
            entity_data={"statements": {"P31": [], "P21": [], "P27": []}}
        )
        mock_handler_class.return_value = mock_handler

        result = await get_batch_statements(self.mock_request, "Q42", "P31,P21")

        expected = {"P31": [], "P21": []}
        assert result["Q42"] == expected

    @patch("models.rest_api.entitybase.routes.batch.EntityReadHandler")
    async def test_get_batch_statements_exception(self, mock_handler_class):
        """Test batch statements handles entity read exceptions."""
        mock_handler = Mock()
        mock_handler.get_entity.side_effect = Exception("Read error")
        mock_handler_class.return_value = mock_handler

        result = await get_batch_statements(self.mock_request, "Q42")

        assert result["Q42"] == {}

    async def test_get_batch_sitelinks_success(self):
        """Test successful batch sitelinks retrieval."""
        self.mock_s3.load_sitelink_metadata.side_effect = (
            lambda h: f"Title{h}" if h % 2 == 0 else None
        )

        result = await get_batch_sitelinks("100,200,300", self.mock_request)

        expected = {"200": "Title200", "300": "Title300"}  # 100 returns None
        assert result == expected

    async def test_get_batch_sitelinks_too_many_hashes(self):
        """Test get_batch_sitelinks raises error for too many hashes."""
        hashes = ",".join([str(i) for i in range(21)])
        with pytest.raises(HTTPException) as exc_info:
            await get_batch_sitelinks(hashes, self.mock_request)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Too many hashes (max 20)"

    async def test_get_batch_sitelinks_invalid_hash(self):
        """Test get_batch_sitelinks skips invalid hashes."""
        result = await get_batch_sitelinks("100,invalid,200", self.mock_request)

        # Should only process valid hashes
        assert "invalid" not in result

    async def test_get_batch_labels_success(self):
        """Test successful batch labels retrieval."""

        def mock_load_metadata(key, hash_val):
            if key == "labels":
                if hash_val == 200:
                    return {"en": {"value": "Label200"}}
                elif hash_val == 300:
                    return {"en": {"value": "Label300"}}
            return None

        self.mock_s3.load_metadata.side_effect = mock_load_metadata

        result = await get_batch_labels("100,200,300", self.mock_request)

        expected = {
            "200": {"en": {"value": "Label200"}},
            "300": {"en": {"value": "Label300"}},
        }
        assert result == expected

    async def test_get_batch_descriptions_success(self):
        """Test successful batch descriptions retrieval."""

        def mock_load_metadata(key, hash_val):
            if key == "descriptions":
                if hash_val == 150:
                    return {"en": {"value": "Desc150"}}
                elif hash_val == 250:
                    return {"en": {"value": "Desc250"}}
            return None

        self.mock_s3.load_metadata.side_effect = mock_load_metadata

        result = await get_batch_descriptions("50,150,250", self.mock_request)

        expected = {
            "150": {"en": {"value": "Desc150"}},
            "250": {"en": {"value": "Desc250"}},
        }
        assert result == expected

    async def test_get_batch_aliases_success(self):
        """Test successful batch aliases retrieval."""

        def mock_load_metadata(key, hash_val):
            if key == "aliases":
                if hash_val == 100:
                    return [{"language": "en", "value": "Alias100"}]
                elif hash_val == 200:
                    return [
                        {"language": "en", "value": "Alias200-1"},
                        {"language": "es", "value": "Alias200-2"},
                    ]
            return None

        self.mock_s3.load_metadata.side_effect = mock_load_metadata

        result = await get_batch_aliases("100,200", self.mock_request)

        expected = {
            "100": [{"language": "en", "value": "Alias100"}],
            "200": [
                {"language": "en", "value": "Alias200-1"},
                {"language": "es", "value": "Alias200-2"},
            ],
        }
        assert result == expected

    async def test_get_batch_aliases_no_aliases(self):
        """Test batch aliases when no aliases found."""
        self.mock_s3.load_metadata.return_value = None

        result = await get_batch_aliases("100", self.mock_request)

        assert result == {}

    async def test_get_batch_labels_too_many_hashes(self):
        """Test get_batch_labels raises error for too many hashes."""
        hashes = ",".join([str(i) for i in range(21)])
        with pytest.raises(HTTPException) as exc_info:
            await get_batch_labels(hashes, self.mock_request)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Too many hashes (max 20)"

    async def test_get_batch_descriptions_too_many_hashes(self):
        """Test get_batch_descriptions raises error for too many hashes."""
        hashes = ",".join([str(i) for i in range(21)])
        with pytest.raises(HTTPException) as exc_info:
            await get_batch_descriptions(hashes, self.mock_request)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Too many hashes (max 20)"

    async def test_get_batch_aliases_too_many_hashes(self):
        """Test get_batch_aliases raises error for too many hashes."""
        hashes = ",".join([str(i) for i in range(21)])
        with pytest.raises(HTTPException) as exc_info:
            await get_batch_aliases(hashes, self.mock_request)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Too many hashes (max 20)"

    async def test_get_batch_sitelinks_empty_result(self):
        """Test batch sitelinks with no valid results."""
        self.mock_s3.load_sitelink_metadata.return_value = None

        result = await get_batch_sitelinks("100,200", self.mock_request)

        assert result == {}


if __name__ == "__main__":
    unittest.main()
