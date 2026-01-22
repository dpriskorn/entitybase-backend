"""Unit tests for batch routes."""
import unittest
from unittest import TestCase

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from models.rest_api.entitybase.v1.routes.batch import (
    get_batch_sitelinks,
    get_batch_labels,
    get_batch_descriptions,
    get_batch_aliases,
    get_batch_statements,
)


class TestBatchRoutes(TestCase):
    """Unit tests for batch routes."""

    @pytest.mark.asyncio
    async def test_get_batch_sitelinks_success(self) -> None:
        """Test successful batch sitelinks retrieval."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client
        mock_request.app.state.state_handler = mock_state

        # Mock S3 client responses
        mock_s3_client.load_sitelink_metadata.side_effect = lambda h: f"Title{h}" if h in [123, 456] else None

        # Call the endpoint
        result = await get_batch_sitelinks("123,456,789", mock_request)

        # Verify result
        expected = {"123": "Title123", "456": "Title456"}
        assert result == expected

        # Verify S3 client was called correctly
        assert mock_s3_client.load_sitelink_metadata.call_count == 3

    @pytest.mark.asyncio
    async def test_get_batch_sitelinks_too_many_hashes(self) -> None:
        """Test batch sitelinks with too many hashes."""
        mock_request = MagicMock()

        # Create 21 hashes (exceeds limit of 20)
        hashes = ",".join([str(i) for i in range(21)])

        with pytest.raises(HTTPException) as exc_info:
            await get_batch_sitelinks(hashes, mock_request)

        assert exc_info.value.status_code == 400
        assert "Too many hashes" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_batch_sitelinks_invalid_hash(self) -> None:
        """Test batch sitelinks with invalid hash (should be skipped)."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client
        mock_request.app.state.state_handler = mock_state

        # Mock S3 client to return data for valid hash
        mock_s3_client.load_sitelink_metadata.return_value = "ValidTitle"

        # Call with mix of valid and invalid hashes
        result = await get_batch_sitelinks("123,invalid,456", mock_request)

        # Should only return results for valid hashes
        expected = {"123": "ValidTitle", "456": "ValidTitle"}
        assert result == expected

    @pytest.mark.asyncio
    async def test_get_batch_labels_success(self) -> None:
        """Test successful batch labels retrieval."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client
        mock_request.app.state.state_handler = mock_state

        # Mock S3 client responses
        mock_s3_client.load_metadata.side_effect = lambda t, h: f"Label{h}" if t == "labels" and h in [123, 456] else None

        # Call the endpoint
        result = await get_batch_labels("123,456,789", mock_request)

        # Verify result
        expected = {"123": "Label123", "456": "Label456"}
        assert result == expected

        # Verify S3 client was called correctly
        assert mock_s3_client.load_metadata.call_count == 3

    @pytest.mark.asyncio
    async def test_get_batch_descriptions_success(self) -> None:
        """Test successful batch descriptions retrieval."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client
        mock_request.app.state.state_handler = mock_state

        # Mock S3 client responses
        mock_s3_client.load_metadata.side_effect = lambda t, h: f"Description{h}" if t == "descriptions" and h in [123, 456] else None

        # Call the endpoint
        result = await get_batch_descriptions("123,456,789", mock_request)

        # Verify result
        expected = {"123": "Description123", "456": "Description456"}
        assert result == expected

    @pytest.mark.asyncio
    async def test_get_batch_aliases_success(self) -> None:
        """Test successful batch aliases retrieval."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client
        mock_request.app.state.state_handler = mock_state

        # Mock S3 client responses
        mock_aliases = ["Alias1", "Alias2"]
        mock_s3_client.load_metadata.side_effect = lambda t, h: mock_aliases if t == "aliases" and h in [123, 456] else None

        # Call the endpoint
        result = await get_batch_aliases("123,456,789", mock_request)

        # Verify result
        expected = {"123": mock_aliases, "456": mock_aliases}
        assert result == expected

    @pytest.mark.asyncio
    async def test_get_batch_aliases_too_many_hashes(self) -> None:
        """Test batch aliases with too many hashes."""
        mock_request = MagicMock()

        # Create 21 hashes (exceeds limit of 20)
        hashes = ",".join([str(i) for i in range(21)])

        with pytest.raises(HTTPException) as exc_info:
            await get_batch_aliases(hashes, mock_request)

        assert exc_info.value.status_code == 400
        assert "Too many hashes" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_batch_statements_success(self) -> None:
        """Test successful batch statements retrieval."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_request.app.state.state_handler = mock_state

        # Mock entity read handler
        mock_handler = MagicMock()
        mock_entity_response = MagicMock()
        mock_entity_response.entity_data = {
            "statements": {
                "P31": [{"id": "Q5:12345", "mainsnak": {"property": "P31"}}],
                "P17": [{"id": "Q5:67890", "mainsnak": {"property": "P17"}}]
            }
        }
        mock_handler.get_entity.return_value = mock_entity_response

        # Mock the EntityReadHandler import
        with unittest.mock.patch("models.rest_api.entitybase.v1.routes.batch.EntityReadHandler", return_value=mock_handler):
            # Call the endpoint
            result = await get_batch_statements(mock_request, "Q5", "P31,P17")

            # Verify result
            expected = {
                "Q5": {
                    "P31": [{"id": "Q5:12345", "mainsnak": {"property": "P31"}}],
                    "P17": [{"id": "Q5:67890", "mainsnak": {"property": "P17"}}]
                }
            }
            assert result == expected

    @pytest.mark.asyncio
    async def test_get_batch_statements_no_properties_filter(self) -> None:
        """Test batch statements without property filtering."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_request.app.state.state_handler = mock_state

        # Mock entity read handler
        mock_handler = MagicMock()
        mock_entity_response = MagicMock()
        mock_entity_response.entity_data = {
            "statements": {
                "P31": [{"id": "Q5:12345", "mainsnak": {"property": "P31"}}],
                "P17": [{"id": "Q5:67890", "mainsnak": {"property": "P17"}}]
            }
        }
        mock_handler.get_entity.return_value = mock_entity_response

        # Mock the EntityReadHandler import
        with unittest.mock.patch("models.rest_api.entitybase.v1.routes.batch.EntityReadHandler", return_value=mock_handler):
            # Call the endpoint without property filter
            result = await get_batch_statements(mock_request, "Q5", "")

            # Verify result contains all statements
            assert "Q5" in result
            assert "P31" in result["Q5"]
            assert "P17" in result["Q5"]

    @pytest.mark.asyncio
    async def test_get_batch_statements_too_many_entities(self) -> None:
        """Test batch statements with too many entities."""
        mock_request = MagicMock()

        # Create 21 entity IDs (exceeds limit of 20)
        entity_ids = ",".join([f"Q{i}" for i in range(21)])

        with pytest.raises(HTTPException) as exc_info:
            await get_batch_statements(mock_request, entity_ids, "")

        assert exc_info.value.status_code == 400
        assert "Too many entities" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_batch_statements_entity_not_found(self) -> None:
        """Test batch statements when entity is not found."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_request.app.state.state_handler = mock_state

        # Mock entity read handler to raise exception
        mock_handler = MagicMock()
        mock_handler.get_entity.side_effect = Exception("Entity not found")

        # Mock the EntityReadHandler import
        with unittest.mock.patch("models.rest_api.entitybase.v1.routes.batch.EntityReadHandler", return_value=mock_handler):
            # Call the endpoint
            result = await get_batch_statements(mock_request, "Q999", "")

            # Should return empty dict for missing entity
            assert result == {"Q999": {}}