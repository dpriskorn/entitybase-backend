"""Unit tests for statements."""
from unittest import TestCase

from models.data.rest_api.v1.entitybase.response import StatementsHashResponse


class TestStatements(TestCase):
    """Placeholder test class for statements."""

    def test_statements_hash_response_serialization(self):
        """Test that StatementsHashResponse serializes correctly."""
        response = StatementsHashResponse(hashes=[123456789, 987654321])
        json_data = response.model_dump(by_alias=True)
        assert "hashes" in json_data
        assert json_data["hashes"] == [123456789, 987654321]
