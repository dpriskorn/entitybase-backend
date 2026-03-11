"""Unit tests for snak_handler."""

from unittest.mock import MagicMock, patch

import pytest

from models.rest_api.entitybase.v1.services.snak_handler import SnakHandler
from models.rest_api.utils import raise_validation_error


class TestSnakHandler:
    """Unit tests for SnakHandler."""

    def setup_method(self):
        """Set up test fixtures."""
        state = MagicMock()
        state.s3_client = MagicMock()

        self.handler = SnakHandler(state=state)

    @patch("models.rest_api.entitybase.v1.services.snak_handler.MetadataExtractor")
    @patch("models.rest_api.entitybase.v1.services.snak_handler.datetime")
    def test_store_snak_success(self, mock_datetime, mock_extractor):
        """Test successful snak storage."""
        mock_extractor.hash_string.return_value = 12345
        mock_datetime.now.return_value.strftime.return_value = "2024-01-01T00:00:00Z"

        from models.data.rest_api.v1.entitybase.request import SnakRequest
        from wikibaseintegrator.models.snaks import Snak

        snak_request = SnakRequest(
            property_id="P31",
            value={"type": "value", "value": "test"},
        )

        self.handler.store_snak(snak_request)

        mock_extractor.hash_string.assert_called_once()
        self.handler.state.s3_client.store_snak.assert_called_once()

    @patch("models.rest_api.entitybase.v1.services.snak_handler.MetadataExtractor")
    @patch("models.rest_api.entitybase.v1.services.snak_handler.datetime")
    def test_store_snak_s3_error(self, mock_datetime, mock_extractor):
        """Test snak storage when S3 client raises error."""
        mock_extractor.hash_string.return_value = 12345
        mock_datetime.now.return_value.strftime.return_value = "2024-01-01T00:00:00Z"

        from models.data.rest_api.v1.entitybase.request import SnakRequest

        snak_request = SnakRequest(
            property_id="P31",
            value={"type": "value", "value": "test"},
        )

        self.handler.state.s3_client.store_snak.side_effect = Exception("S3 error")

        with pytest.raises(Exception):
            self.handler.store_snak(snak_request)

    def test_get_snak_success(self):
        """Test successful snak retrieval."""
        from models.data.infrastructure.s3.snak_data import S3SnakData

        mock_snak_data = S3SnakData(
            schema="1.0.0",
            snak={"property": {"id": "P31"}},
            hash=12345,
            created_at="2024-01-01T00:00:00Z",
        )

        self.handler.state.s3_client.load_snak.return_value = mock_snak_data

        result = self.handler.get_snak(12345)

        assert result is not None
        self.handler.state.s3_client.load_snak.assert_called_once_with(12345)

    def test_get_snak_not_found(self):
        """Test snak retrieval when not found."""
        self.handler.state.s3_client.load_snak.return_value = None

        result = self.handler.get_snak(12345)

        assert result is None

    def test_get_snak_s3_error(self):
        """Test snak retrieval when S3 client raises error."""
        self.handler.state.s3_client.load_snak.side_effect = Exception("S3 error")

        result = self.handler.get_snak(12345)

        assert result is None

    @patch("models.rest_api.entitybase.v1.services.snak_handler.MetadataExtractor")
    @patch("models.rest_api.entitybase.v1.services.snak_handler.datetime")
    def test_store_snak_json_serialization(self, mock_datetime, mock_extractor):
        """Test that snak is JSON serialized correctly."""
        mock_extractor.hash_string.return_value = 12345
        mock_datetime.now.return_value.strftime.return_value = "2024-01-01T00:00:00Z"

        from models.data.rest_api.v1.entitybase.request import SnakRequest

        snak_request = SnakRequest(
            property_id="P31",
            value={"type": "value", "value": "test"},
        )

        result = self.handler.store_snak(snak_request)

        assert result == 12345
        call_args = self.handler.state.s3_client.store_snak.call_args
        stored_data = call_args[0][1]
        assert stored_data.hash == 12345

    def test_get_snak_returns_none_on_exception(self):
        """Test that get_snak returns None on any exception."""
        self.handler.state.s3_client.load_snak.side_effect = RuntimeError("Error")

        result = self.handler.get_snak(12345)

        assert result is None

    @patch("models.rest_api.entitybase.v1.services.snak_handler.MetadataExtractor")
    @patch("models.rest_api.entitybase.v1.services.snak_handler.datetime")
    def test_store_snak_calls_s3_with_correct_hash(self, mock_datetime, mock_extractor):
        """Test that store_snak calls S3 client with the correct hash."""
        mock_extractor.hash_string.return_value = 99999
        mock_datetime.now.return_value.strftime.return_value = "2024-01-01T00:00:00Z"

        from models.data.rest_api.v1.entitybase.request import SnakRequest

        snak_request = SnakRequest(
            property_id="P569",
            value={"type": "time", "time": "+2024-01-01T00:00:00Z"},
        )

        result = self.handler.store_snak(snak_request)

        assert result == 99999
        self.handler.state.s3_client.store_snak.assert_called_with(
            99999, pytest.approx(any)
        )
