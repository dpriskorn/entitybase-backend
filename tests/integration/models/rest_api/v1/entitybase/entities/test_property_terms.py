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

        response = await client.get(f"{api_prefix}/entities/P70001/labels/en")
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

        response = await client.get(f"{api_prefix}/entities/P70002/labels/de")
        assert response.status_code == 404


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

        response = await client.get(f"{api_prefix}/entities/P70003/descriptions/en")
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

        response = await client.get(f"{api_prefix}/entities/P70004/descriptions/de")
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_property_aliases_success(api_prefix: str) -> None:
    """Test getting property aliases for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="P70005",
        type="property",
        aliases={
            "en": [
                {"language": "en", "value": "Property Alias 1"},
                {"language": "en", "value": "Property Alias 2"},
            ]
        },
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

        response = await client.get(f"{api_prefix}/entities/P70005/aliases/en")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0] == "Property Alias 1"
        assert data[1] == "Property Alias 2"


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

        response = await client.get(f"{api_prefix}/entities/P70006/aliases/de")
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_property_aliases_replace(api_prefix: str) -> None:
    """Test updating property aliases replaces existing ones."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="P70007",
        type="property",
        aliases={
            "en": [
                {"language": "en", "value": "Old Alias 1"},
                {"language": "en", "value": "Old Alias 2"},
            ]
        },
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
            f"{api_prefix}/entities/P70007/aliases/en",
            json=["New Alias 1", "New Alias 2"],
            headers={"X-Edit-Summary": "replace property aliases", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "hashes" in data
        response = await client.get(f"{api_prefix}/entities/P70007/aliases/en")
        assert response.status_code == 200
        aliases = response.json()
        assert len(aliases) == 2
        assert "New Alias 1" in aliases
        assert "New Alias 2" in aliases


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
            f"{api_prefix}/entities/P70008/aliases/en",
            json=["Property Alias 1", "Property Alias 2"],
            headers={"X-Edit-Summary": "add property aliases", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "hashes" in data
        assert len(data["hashes"]) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_property_label_success(api_prefix: str) -> None:
    """Test updating property label for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="P70009",
        type="property",
        labels={"en": {"language": "en", "value": "Original Label"}},
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
            f"{api_prefix}/entities/P70009/labels/en",
            json={"language": "en", "value": "Updated Label"},
            headers={"X-Edit-Summary": "update label", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "hash" in data
        response = await client.get(f"{api_prefix}/entities/P70009/labels/en")
        assert response.status_code == 200
        assert response.json()["value"] == "Updated Label"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_property_description_success(api_prefix: str) -> None:
    """Test updating property description for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="P70010",
        type="property",
        descriptions={"en": {"language": "en", "value": "Original Description"}},
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
            f"{api_prefix}/entities/P70010/descriptions/en",
            json={"language": "en", "value": "Updated Description"},
            headers={"X-Edit-Summary": "update description", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "hash" in data
        response = await client.get(f"{api_prefix}/entities/P70010/descriptions/en")
        assert response.status_code == 200
        assert response.json()["value"] == "Updated Description"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_property_label_success(api_prefix: str) -> None:
    """Test deleting property label for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="P70011",
        type="property",
        labels={
            "en": {"language": "en", "value": "Label to Delete"},
            "de": {"language": "de", "value": "German Label"},
        },
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

        response = await client.delete(
            f"{api_prefix}/entities/P70011/labels/en",
            headers={"X-Edit-Summary": "delete label", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_property_description_success(api_prefix: str) -> None:
    """Test deleting property description for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="P70012",
        type="property",
        descriptions={
            "en": {"language": "en", "value": "Description to Delete"},
            "de": {"language": "de", "value": "German Description"},
        },
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

        response = await client.delete(
            f"{api_prefix}/entities/P70012/descriptions/en",
            headers={"X-Edit-Summary": "delete description", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_property_aliases_success(api_prefix: str) -> None:
    """Test deleting all property aliases for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="P70013",
        type="property",
        aliases={
            "en": [
                {"language": "en", "value": "Alias 1"},
                {"language": "en", "value": "Alias 2"},
            ],
            "de": [{"language": "de", "value": "Alias DE"}],
        },
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

        response = await client.delete(
            f"{api_prefix}/entities/P70013/aliases/en",
            headers={"X-Edit-Summary": "delete english aliases", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
