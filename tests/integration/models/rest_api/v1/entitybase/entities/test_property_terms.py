import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient

from models.data.rest_api.v1.entitybase.request import EntityCreateRequest

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_property_label_success(api_prefix: str) -> None:
    """Test getting property label for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="P70001",
        type="property",
        labels={"en": {"language": "en", "value": "Test Property Label"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test property", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(
            f"{api_prefix}/entities/properties/P70001/labels/en"
        )
        assert response.status_code == 200
        data = response.json()
        assert "value" in data
        assert data["value"] == "Test Property Label"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_property_label_not_found(api_prefix: str) -> None:
    """Test getting property label for non-existent language returns 404."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="P70002",
        type="property",
        labels={"en": {"language": "en", "value": "Test Property Label"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test property", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(
            f"{api_prefix}/entities/properties/P70002/labels/de"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["message"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_property_description_success(api_prefix: str) -> None:
    """Test getting property description for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="P70003",
        type="property",
        descriptions={"en": {"language": "en", "value": "Test Property Description"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test property", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(
            f"{api_prefix}/entities/properties/P70003/descriptions/en"
        )
        assert response.status_code == 200
        data = response.json()
        assert "value" in data
        assert data["value"] == "Test Property Description"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_property_description_not_found(api_prefix: str) -> None:
    """Test getting property description for non-existent language returns 404."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="P70004",
        type="property",
        descriptions={"en": {"language": "en", "value": "Test Property Description"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test property", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(
            f"{api_prefix}/entities/properties/P70004/descriptions/de"
        )
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_property_aliases_success(api_prefix: str) -> None:
    """Test getting property aliases for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="P70005",
        type="property",
        aliases={"en": [{"language": "en", "value": "Property Alias 1"}, {"language": "en", "value": "Property Alias 2"}]},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test property", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(
            f"{api_prefix}/entities/properties/P70005/aliases/en"
        )
        assert response.status_code == 200
        data = response.json()
        assert "aliases" in data
        assert len(data["aliases"]) == 2
        assert data["aliases"][0]["value"] == "Property Alias 1"
        assert data["aliases"][1]["value"] == "Property Alias 2"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_property_aliases_not_found(api_prefix: str) -> None:
    """Test getting property aliases for non-existent language returns 404."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="P70006",
        type="property",
        aliases={"en": [{"language": "en", "value": "Test Alias"}]},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test property", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(
            f"{api_prefix}/entities/properties/P70006/aliases/de"
        )
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_property_aliases_replace(api_prefix: str) -> None:
    """Test updating property aliases replaces existing ones."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="P70007",
        type="property",
        aliases={"en": [{"language": "en", "value": "Old Alias 1"}, {"language": "en", "value": "Old Alias 2"}]},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test property", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.put(
            f"{api_prefix}/entities/properties/P70007/aliases/en",
            json=["New Alias 1", "New Alias 2"],
            headers={"X-Edit-Summary": "replace property aliases", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        aliases = data["data"]["aliases"]["en"]
        assert len(aliases) == 2
        assert aliases[0]["value"] == "New Alias 1"
        assert aliases[1]["value"] == "New Alias 2"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_property_aliases_add(api_prefix: str) -> None:
    """Test updating property aliases creates new if not exists."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="P70008",
        type="property",
        labels={"en": {"language": "en", "value": "Test Property"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/properties",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test property", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.put(
            f"{api_prefix}/entities/properties/P70008/aliases/en",
            json=["Property Alias 1", "Property Alias 2"],
            headers={"X-Edit-Summary": "add property aliases", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "en" in data["data"]["aliases"]
        assert len(data["data"]["aliases"]["en"]) == 2
