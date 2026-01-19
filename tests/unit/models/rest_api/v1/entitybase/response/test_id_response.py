import pytest

pytestmark = pytest.mark.unit

from models.rest_api.entitybase.v1.response.id_response import IdResponse


class TestIdResponse:
    def test_id_response_creation(self) -> None:
        """Test creating IdResponse with valid ID."""
        response = IdResponse(id="Q123")
        assert response.id == "Q123"

    def test_id_response_property_id(self) -> None:
        """Test creating IdResponse with property ID."""
        response = IdResponse(id="P456")
        assert response.id == "P456"

    def test_id_response_validation(self) -> None:
        """Test IdResponse requires id field."""
        with pytest.raises(ValueError):
            IdResponse()
