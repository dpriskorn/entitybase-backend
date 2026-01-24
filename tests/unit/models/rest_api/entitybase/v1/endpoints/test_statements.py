"""Unit tests for statements."""

from models.data.rest_api.v1.entitybase.response import StatementsHashResponse


class TestStatements:
    """Placeholder test class for statements."""

    def test_statements_hash_response_serialization():
        """Test that StatementsHashResponse serializes correctly."""
        response = StatementsHashResponse(property_hashes=[123456789, 987654321])
        json_data = response.model_dump()
        assert "hashes" in json_data
        assert json_data["hashes"] == [123456789, 987654321]
