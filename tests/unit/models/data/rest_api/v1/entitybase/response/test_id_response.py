"""Unit tests for ID response model."""

import pytest

from models.data.rest_api.v1.entitybase.response.id_response import IdResponse


class TestIdResponse:
    """Unit tests for IdResponse model."""

    def test_basic_instantiation(self):
        """Test basic instantiation."""
        response = IdResponse(id="Q123")
        assert response.id == "Q123"

    def test_property_id(self):
        """Test with property ID."""
        response = IdResponse(id="P456")
        assert response.id == "P456"

    def test_model_dump(self):
        """Test model_dump()."""
        response = IdResponse(id="Q789")
        dumped = response.model_dump()
        assert dumped == {"id": "Q789"}

    def test_model_dump_json(self):
        """Test model_dump_json()."""
        response = IdResponse(id="L100")
        json_str = response.model_dump_json()
        assert "L100" in json_str
