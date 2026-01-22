"""Unit tests for snak_handler."""

from unittest.mock import MagicMock, patch

import pytest

from models.rest_api.entitybase.v1.services.snak_handler import SnakHandler
from models.data.infrastructure.s3.snak_data import S3SnakData


class TestSnakHandler:
    """Unit tests for SnakHandler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.s3_client = MagicMock()
        self.handler = SnakHandler(self.s3_client)

    @patch('models.rest_api.entitybase.v1.services.snak_handler.MetadataExtractor')
    @patch('models.rest_api.entitybase.v1.services.snak_handler.datetime')
    def test_store_snak_success(self, mock_datetime, mock_extractor):
        """Test successful snak storage."""
        mock_datetime.now.return_value.strftime.return_value = "2023-01-01T12:00:00Z"
        mock_extractor.hash_string.return_value = 12345

        snak = {"property": "P31", "datavalue": {"type": "wikibase-entityid", "value": {"id": "Q5"}}}

        result = self.handler.store_snak(snak)

        assert result == 12345

        # Verify S3 client call
        self.s3_client.store_snak.assert_called_once()
        call_args = self.s3_client.store_snak.call_args
        assert call_args[0][0] == 12345  # content_hash

        snak_data = call_args[0][1]
        assert isinstance(snak_data, S3SnakData)
        assert snak_data.schema == "1.0.0"
        assert snak_data.snak == snak
        assert snak_data.hash == 12345
        assert snak_data.created_at == "2023-01-01T12:00:00Z"

    @patch('models.rest_api.entitybase.v1.services.snak_handler.MetadataExtractor')
    def test_store_snak_s3_error(self, mock_extractor):
        """Test snak storage when S3 client raises error."""
        mock_extractor.hash_string.return_value = 12345
        self.s3_client.store_snak.side_effect = Exception("S3 storage failed")

        snak = {"property": "P31", "datavalue": {"type": "wikibase-entityid", "value": {"id": "Q5"}}}

        with pytest.raises(Exception) as exc_info:
            self.handler.store_snak(snak)

        assert "Failed to store snak: S3 storage failed" in str(exc_info.value)

    def test_get_snak_success(self):
        """Test successful snak retrieval."""
        mock_snak_data = MagicMock()
        mock_snak_data.snak = {"property": "P31", "datavalue": {"type": "wikibase-entityid", "value": {"id": "Q5"}}}
        self.s3_client.load_snak.return_value = mock_snak_data

        result = self.handler.get_snak(12345)

        assert result == mock_snak_data.snak
        self.s3_client.load_snak.assert_called_once_with(12345)

    def test_get_snak_not_found(self):
        """Test snak retrieval when not found."""
        self.s3_client.load_snak.return_value = None

        result = self.handler.get_snak(12345)

        assert result is None
        self.s3_client.load_snak.assert_called_once_with(12345)

    def test_get_snak_s3_error(self):
        """Test snak retrieval when S3 client raises error."""
        self.s3_client.load_snak.side_effect = Exception("S3 load failed")

        result = self.handler.get_snak(12345)

        assert result is None
        self.s3_client.load_snak.assert_called_once_with(12345)

    @patch('models.rest_api.entitybase.v1.services.snak_handler.MetadataExtractor')
    @patch('models.rest_api.entitybase.v1.services.snak_handler.json')
    def test_store_snak_json_dumps(self, mock_json, mock_extractor):
        """Test that snak is JSON serialized with sorted keys."""
        mock_extractor.hash_string.return_value = 12345
        mock_json.dumps.return_value = '{"property":"P31"}'

        snak = {"datavalue": {"type": "wikibase-entityid", "value": {"id": "Q5"}}, "property": "P31"}

        self.handler.store_snak(snak)

        mock_json.dumps.assert_called_once_with(snak, sort_keys=True)
        mock_extractor.hash_string.assert_called_once_with('{"property":"P31"}')

    def test_get_snak_returns_none_on_exception(self):
        """Test that get_snak returns None on any exception."""
        self.s3_client.load_snak.side_effect = RuntimeError("Unexpected error")

        result = self.handler.get_snak(99999)

        assert result is None
