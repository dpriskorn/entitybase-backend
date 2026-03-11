"""Unit tests for snak_handler."""

from unittest.mock import MagicMock, patch

import pytest

from models.rest_api.entitybase.v1.services.snak_handler import SnakHandler


class TestSnakHandler:
    """Unit tests for SnakHandler."""

    def setup_method(self):
        """Set up test fixtures."""
        state = MagicMock()
        state.s3_client = MagicMock()

        self.handler = SnakHandler(state=state)

    def test_get_snak_success(self):
        """Test successful snak retrieval."""
        from models.data.infrastructure.s3.snak_data import S3SnakData
        from unittest.mock import MagicMock as MockSnak

        mock_snak_data = S3SnakData(
            schema="1.0.0",
            snak={"snaktype": "value", "property": {"id": "P31"}, "datavalue": {"type": "string", "value": "test"}},
            hash=12345,
            created_at="2024-01-01T00:00:00Z",
        )

        self.handler.state.s3_client.load_snak.return_value = mock_snak_data

        result = self.handler.get_snak(12345)

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

    def test_get_snak_returns_none_on_exception(self):
        """Test that get_snak returns None on any exception."""
        self.handler.state.s3_client.load_snak.side_effect = RuntimeError("Error")

        result = self.handler.get_snak(12345)

        assert result is None

    def test_handler_has_state(self):
        """Test that handler has state attribute."""
        assert hasattr(self.handler, "state")

    def test_handler_has_store_snak_method(self):
        """Test that handler has store_snak method."""
        assert hasattr(self.handler, "store_snak")
        assert callable(self.handler.store_snak)

    def test_handler_has_get_snak_method(self):
        """Test that handler has get_snak method."""
        assert hasattr(self.handler, "get_snak")
        assert callable(self.handler.get_snak)
