"""Unit tests for references endpoint."""

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from models.data.infrastructure.s3.reference_data import S3ReferenceData
from models.rest_api.entitybase.v1.endpoints.references import get_references
from models.data.rest_api.v1.response import ReferenceResponse


class TestReferencesEndpoint:
    """Unit tests for references endpoint handler."""

    @pytest.mark.asyncio
    async def test_get_references_single_valid_hash(self) -> None:
        """Test fetching a single valid reference."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client
        mock_request.app.state.state_handler = mock_state

        # Mock reference data
        mock_reference_data = S3ReferenceData(
            reference={
                "snaks": {
                    "P854": [
                        {
                            "snaktype": "value",
                            "property": "P854",
                            "datavalue": {
                                "value": "https://example.com",
                                "type": "string",
                            },
                            "datatype": "url",
                        }
                    ]
                },
                "snaks-order": ["P854"]
            },
            hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )

        mock_s3_client.load_references_batch.return_value = [mock_reference_data]

        # Call the endpoint
        result = await get_references(mock_request, "12345")

        # Verify result
        assert len(result) == 1
        assert isinstance(result[0], ReferenceResponse)
        assert result[0].reference == mock_reference_data.reference
        assert result[0].content_hash == mock_reference_data.content_hash
        assert result[0].created_at == mock_reference_data.created_at

        # Verify S3 client was called correctly
        mock_s3_client.load_references_batch.assert_called_once_with([12345])

    @pytest.mark.asyncio
    async def test_get_references_batch_mixed_results(self) -> None:
        """Test fetching multiple references with some missing."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client
        mock_request.app.state.state_handler = mock_state

        # Mock reference data - first found, second missing
        mock_reference_data = S3ReferenceData(
            reference={"snaks": {"P854": []}, "snaks-order": []},
            hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )

        mock_s3_client.load_references_batch.return_value = [mock_reference_data, None]

        # Call the endpoint
        result = await get_references(mock_request, "12345,67890")

        # Verify result
        assert len(result) == 2
        assert isinstance(result[0], ReferenceResponse)
        assert result[1] is None

        # Verify S3 client was called correctly
        mock_s3_client.load_references_batch.assert_called_once_with([12345, 67890])

    @pytest.mark.asyncio
    async def test_get_references_invalid_hash_format(self) -> None:
        """Test endpoint with invalid hash format."""
        mock_request = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_references(mock_request, "invalid-hash")

        assert exc_info.value.status_code == 400
        assert "Invalid hash format" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_references_too_many_hashes(self) -> None:
        """Test endpoint with too many hashes."""
        mock_request = MagicMock()

        # Create 101 hashes (exceeds limit of 100)
        hashes = ",".join([str(i) for i in range(101)])

        with pytest.raises(HTTPException) as exc_info:
            await get_references(mock_request, hashes)

        assert exc_info.value.status_code == 400
        assert "Too many hashes" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_references_no_hashes_provided(self) -> None:
        """Test endpoint with no hashes provided."""
        mock_request = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_references(mock_request, ",,,")

        assert exc_info.value.status_code == 400
        assert "No hashes provided" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_references_empty_hash_string(self) -> None:
        """Test endpoint with empty hash string."""
        mock_request = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_references(mock_request, "")

        assert exc_info.value.status_code == 400
        assert "No hashes provided" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_references_s3_client_error(self) -> None:
        """Test endpoint when S3 client raises an error."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client
        mock_request.app.state.state_handler = mock_state

        # Mock S3 client to raise an exception
        mock_s3_client.load_references_batch.side_effect = Exception("S3 connection error")

        with pytest.raises(HTTPException) as exc_info:
            await get_references(mock_request, "12345")

        assert exc_info.value.status_code == 500
        assert "Internal server error" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_references_large_batch_all_missing(self) -> None:
        """Test large batch where all references are missing."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client
        mock_request.app.state.state_handler = mock_state

        # Mock all references as missing
        mock_s3_client.load_references_batch.return_value = [None, None, None]

        # Call the endpoint with 3 hashes
        result = await get_references(mock_request, "12345,67890,11111")

        # Verify result
        assert len(result) == 3
        assert all(item is None for item in result)

    @pytest.mark.asyncio
    async def test_get_references_whitespace_handling(self) -> None:
        """Test that whitespace in hash strings is properly handled."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client
        mock_request.app.state.state_handler = mock_state

        # Mock reference data
        mock_reference_data = S3ReferenceData(
            reference={"snaks": {"P854": []}, "snaks-order": []},
            hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )

        mock_s3_client.load_references_batch.return_value = [mock_reference_data]

        # Call the endpoint with whitespace around hashes
        result = await get_references(mock_request, " 12345 ")

        # Verify result
        assert len(result) == 1
        assert isinstance(result[0], ReferenceResponse)

        # Verify S3 client was called with clean integer
        mock_s3_client.load_references_batch.assert_called_once_with([12345])