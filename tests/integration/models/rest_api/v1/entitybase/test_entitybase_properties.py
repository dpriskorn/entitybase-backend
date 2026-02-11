import pytest
from httpx import ASGITransport, AsyncClient


from models.rest_api.main import app


@pytest.mark.asyncio
@pytest.mark.integration
async def test_entitybase_create_property(api_prefix: str) -> None:
    """Test creating a property via entitybase endpoint."""
    data = {
        "type": "property",
        "labels": {"en": {"language": "en", "value": "Test Property"}},
        "descriptions": {"en": {"language": "en", "value": "A test property"}},
        "datatype": "string",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(f"{api_prefix}/entities/properties", json=data)
        assert response.status_code == 201  # Created

        response_data = response.json()
        assert "id" in response_data
        assert response_data["id"].startswith("P")
        assert response_data["type"] == "property"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_entitybase_create_property_minimal(api_prefix: str) -> None:
    """Test creating a property with minimal required fields."""
    data = {
        "type": "property",
        "labels": {"en": {"language": "en", "value": "Minimal Property"}},
        "datatype": "wikibase-item",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(f"{api_prefix}/entities/properties", json=data)
        assert response.status_code == 201

        response_data = response.json()
        assert "id" in response_data
        assert response_data["id"].startswith("P")
        assert response_data["type"] == "property"
        assert response_data["labels"]["en"]["value"] == "Minimal Property"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_entitybase_create_property_invalid(api_prefix: str) -> None:
    """Test creating a property with invalid data."""
    data = {
        "type": "property",
        "labels": {},  # Missing labels
        "datatype": "string",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(f"{api_prefix}/entities/properties", json=data)
        # Should fail validation
        assert response.status_code == 400
