"""Unit tests for qualifiers endpoint."""

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from models.data.infrastructure.s3.qualifier_data import S3QualifierData
from models.rest_api.entitybase.v1.endpoints.qualifiers import get_qualifiers
from models.data.rest_api.v1.response import QualifierResponse


class TestQualifiersEndpoint:
    """Unit tests for qualifiers endpoint handler."""

    @pytest.mark.asyncio
    async def test_get_qualifiers_single_valid_hash(self) -> None:
        """Test fetching a single valid qualifier."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client
        mock_request.app.state.state_handler = mock_state

        # Mock qualifier data
        mock_qualifier_data = S3QualifierData(
            qualifier={
                "P580": [
                    {
                        "snaktype": "value",
                        "property": "P580",
                        "datatype": "time",
                        "datavalue": {
                            "value": {
                                "time": "+2023-01-01T00:00:00Z",
                                "timezone": 0,
                                "before": 0,
                                "after": 0,
                                "precision": 11,
                                "calendarmodel": "http://www.wikidata.org/entity/Q1985727",
                            },
                            "type": "time",
                        },
                    }
                ]
            },
            hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )

        mock_s3_client.load_qualifiers_batch.return_value = [mock_qualifier_data]

        # Call the endpoint
        result = await get_qualifiers(mock_request, "12345")

        # Verify result
        assert len(result) == 1
        assert isinstance(result[0], QualifierResponse)
        assert result[0].qualifier == mock_qualifier_data.qualifier
        assert result[0].content_hash == mock_qualifier_data.content_hash
        assert result[0].created_at == mock_qualifier_data.created_at

        # Verify S3 client was called correctly
        mock_s3_client.load_qualifiers_batch.assert_called_once_with([12345])

    @pytest.mark.asyncio
    async def test_get_qualifiers_batch_mixed_results(self) -> None:
        """Test fetching multiple qualifiers with some missing."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client
        mock_request.app.state.state_handler = mock_state

        # Mock qualifier data - first found, second missing
        mock_qualifier_data = S3QualifierData(
            qualifier={"P580": []},
            hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )

        mock_s3_client.load_qualifiers_batch.return_value = [mock_qualifier_data, None]

        # Call the endpoint
        result = await get_qualifiers(mock_request, "12345,67890")

        # Verify result
        assert len(result) == 2
        assert isinstance(result[0], QualifierResponse)
        assert result[1] is None

        # Verify S3 client was called correctly
        mock_s3_client.load_qualifiers_batch.assert_called_once_with([12345, 67890])

    @pytest.mark.asyncio
    async def test_get_qualifiers_invalid_hash_format(self) -> None:
        """Test endpoint with invalid hash format."""
        mock_request = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_qualifiers(mock_request, "invalid-hash")

        assert exc_info.value.status_code == 400
        assert "Invalid hash format" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_qualifiers_too_many_hashes(self) -> None:
        """Test endpoint with too many hashes."""
        mock_request = MagicMock()

        # Create 101 hashes (exceeds limit of 100)
        hashes = ",".join([str(i) for i in range(101)])

        with pytest.raises(HTTPException) as exc_info:
            await get_qualifiers(mock_request, hashes)

        assert exc_info.value.status_code == 400
        assert "Too many hashes" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_qualifiers_no_hashes_provided(self) -> None:
        """Test endpoint with no hashes provided."""
        mock_request = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_qualifiers(mock_request, ",,,")

        assert exc_info.value.status_code == 400
        assert "No hashes provided" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_qualifiers_empty_hash_string(self) -> None:
        """Test endpoint with empty hash string."""
        mock_request = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_qualifiers(mock_request, "")

        assert exc_info.value.status_code == 400
        assert "No hashes provided" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_qualifiers_s3_client_error(self) -> None:
        """Test endpoint when S3 client raises an error."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client
        mock_request.app.state.state_handler = mock_state

        # Mock S3 client to raise an exception
        mock_s3_client.load_qualifiers_batch.side_effect = Exception("S3 connection error")

        with pytest.raises(HTTPException) as exc_info:
            await get_qualifiers(mock_request, "12345")

        assert exc_info.value.status_code == 500
        assert "Internal server error" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_qualifiers_large_batch_all_missing(self) -> None:
        """Test large batch where all qualifiers are missing."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client
        mock_request.app.state.state_handler = mock_state

        # Mock all qualifiers as missing
        mock_s3_client.load_qualifiers_batch.return_value = [None, None, None]

        # Call the endpoint with 3 hashes
        result = await get_qualifiers(mock_request, "12345,67890,11111")

        # Verify result
        assert len(result) == 3
        assert all(item is None for item in result)

    @pytest.mark.asyncio
    async def test_get_qualifiers_whitespace_handling(self) -> None:
        """Test that whitespace in hash strings is properly handled."""
        # Mock request
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client
        mock_request.app.state.state_handler = mock_state

        # Mock qualifier data
        mock_qualifier_data = S3QualifierData(
            qualifier={"P580": []},
            hash=12345,
            created_at="2023-01-01T12:00:00Z"
        )

        mock_s3_client.load_qualifiers_batch.return_value = [mock_qualifier_data]

        # Call the endpoint with whitespace around hashes
        result = await get_qualifiers(mock_request, " 12345 ")

        # Verify result
        assert len(result) == 1
        assert isinstance(result[0], QualifierResponse)

        # Verify S3 client was called with clean integer
        mock_s3_client.load_qualifiers_batch.assert_called_once_with([12345])