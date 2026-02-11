import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient

from models.data.rest_api.v1.entitybase.request import EntityCreateRequest

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_label_success(api_prefix: str) -> None:
    """Test getting item label for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70001",
        type="item",
        labels={"en": {"value": "Test Label"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        logger.debug(f"sending API post request to {api_prefix}/entities/items")
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        logger.debug("Got 200 response")

        logger.debug(f"sending API get request to {api_prefix}/entities/items/Q70001/labels/en")
        response = await client.get(f"{api_prefix}/entities/items/Q70001/labels/en")
        assert response.status_code == 200
        data = response.json()
        assert "value" in data
        assert data["value"] == "Test Label"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_label_not_found(api_prefix: str) -> None:
    """Test getting item label for non-existent language returns 404."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70002",
        type="item",
        labels={"en": {"value": "Test Label"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/items/Q70002/labels/de")
        assert response.status_code == 404
        assert "not found" in response.json()["message"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_label_multiple_languages(api_prefix: str) -> None:
    """Test getting item labels for multiple languages."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70003",
        type="item",
        labels={
            "en": {"value": "Test English"},
            "de": {"value": "Test German"},
            "fr": {"value": "Test French"},
        },
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        for lang, expected in [
            ("en", "Test English"),
            ("de", "Test German"),
            ("fr", "Test French"),
        ]:
            response = await client.get(f"{api_prefix}/entities/items/Q70003/labels/{lang}")
            assert response.status_code == 200
            data = response.json()
            assert data["value"] == expected


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_label_success(api_prefix: str) -> None:
    """Test updating item label for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70004",
        type="item",
        labels={"en": {"value": "Original Label"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.put(
            f"{api_prefix}/entities/items/Q70004/labels/en",
            json={"language": "en", "value": "Updated Label"},
            headers={"X-Edit-Summary": "update label", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        logger.debug(f"Response data keys: {list(data.keys())}")
        logger.debug(f"Response data['data'] keys: {list(data['data'].keys())}")
        logger.debug(f"Response data['data'] content: {data['data']}")
        assert data["data"]["labels"]["en"]["value"] == "Updated Label"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_label_creates_new(api_prefix: str) -> None:
    """Test updating item label creates new language if not exists."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70005",
        type="item",
        labels={"en": {"value": "Test Label"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.put(
            f"{api_prefix}/entities/items/Q70005/labels/de",
            json={"language": "de", "value": "Neues Label"},
            headers={"X-Edit-Summary": "add german label", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "de" in data["data"]["labels"]
        assert data["data"]["labels"]["de"]["value"] == "Neues Label"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_label_entity_not_found(api_prefix: str) -> None:
    """Test updating item label for non-existent entity returns 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.put(
            f"{api_prefix}/entities/items/Q99999/labels/en",
            json={"language": "en", "value": "Updated Label"},
            headers={"X-Edit-Summary": "update label", "X-User-ID": "0"},
        )
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_item_label_success(api_prefix: str) -> None:
    """Test deleting item label for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70006",
        type="item",
        labels={"en": {"value": "Label to Delete"}, "de": {"value": "German Label"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.delete(
            f"{api_prefix}/entities/items/Q70006/labels/en",
            headers={"X-Edit-Summary": "delete label", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "en" not in data["data"]["labels"]
        assert "de" in data["data"]["labels"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_item_label_not_found(api_prefix: str) -> None:
    """Test deleting non-existent item label returns 404."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70007",
        type="item",
        labels={"en": {"value": "Test Label"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.delete(
            f"{api_prefix}/entities/items/Q70007/labels/de",
            headers={"X-Edit-Summary": "delete label", "X-User-ID": "0"},
        )
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_item_label_entity_not_found(api_prefix: str) -> None:
    """Test deleting item label for non-existent entity returns 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.delete(
            f"{api_prefix}/entities/items/Q99999/labels/en",
            headers={"X-Edit-Summary": "delete label", "X-User-ID": "0"},
        )
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_description_success(api_prefix: str) -> None:
    """Test getting item description for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70008",
        type="item",
        descriptions={"en": {"value": "Test Description"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/items/Q70008/descriptions/en")
        assert response.status_code == 200
        data = response.json()
        assert "value" in data
        assert data["value"] == "Test Description"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_description_not_found(api_prefix: str) -> None:
    """Test getting item description for non-existent language returns 404."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70009",
        type="item",
        descriptions={"en": {"value": "Test Description"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/items/Q70009/descriptions/de")
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_description_success(api_prefix: str) -> None:
    """Test updating item description for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70010",
        type="item",
        descriptions={"en": {"value": "Original Description"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.put(
            f"{api_prefix}/entities/items/Q70010/descriptions/en",
            json={"language": "en", "value": "Updated Description"},
            headers={"X-Edit-Summary": "update description", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["descriptions"]["en"]["value"] == "Updated Description"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_description_creates_new(api_prefix: str) -> None:
    """Test updating item description creates new language if not exists."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70011",
        type="item",
        descriptions={"en": {"value": "Test Description"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.put(
            f"{api_prefix}/entities/items/Q70011/descriptions/de",
            json={"language": "de", "value": "Neue Beschreibung"},
            headers={"X-Edit-Summary": "add german description", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "de" in data["data"]["descriptions"]
        assert data["data"]["descriptions"]["de"]["value"] == "Neue Beschreibung"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_item_description_success(api_prefix: str) -> None:
    """Test deleting item description for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70012",
        type="item",
        descriptions={
            "en": {"value": "Description to Delete"},
            "de": {"value": "German Description"},
        },
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.delete(
            f"{api_prefix}/entities/items/Q70012/descriptions/en",
            headers={"X-Edit-Summary": "delete description", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "en" not in data["data"]["descriptions"]
        assert "de" in data["data"]["descriptions"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_item_description_not_found(api_prefix: str) -> None:
    """Test deleting non-existent item description returns 404."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70013",
        type="item",
        descriptions={"en": {"value": "Test Description"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.delete(
            f"{api_prefix}/entities/items/Q70013/descriptions/de",
            headers={"X-Edit-Summary": "delete description", "X-User-ID": "0"},
        )
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_aliases_success(api_prefix: str) -> None:
    """Test getting item aliases for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70014",
        type="item",
        aliases={"en": [{"value": "Alias 1"}, {"value": "Alias 2"}]},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/items/Q70014/aliases/en")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert "Alias 1" in data
        assert "Alias 2" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_aliases_not_found(api_prefix: str) -> None:
    """Test getting item aliases for non-existent language returns 404."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70015",
        type="item",
        aliases={"en": [{"value": "Test Alias"}]},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/items/Q70015/aliases/de")
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_item_aliases_multiple(api_prefix: str) -> None:
    """Test getting multiple item aliases for language."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70016",
        type="item",
        aliases={
            "en": [{"value": "Alias 1"}, {"value": "Alias 2"}, {"value": "Alias 3"}]
        },
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/items/Q70016/aliases/en")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_aliases_replace(api_prefix: str) -> None:
    """Test updating item aliases replaces existing ones."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70017",
        type="item",
        aliases={"en": [{"value": "Old Alias 1"}, {"value": "Old Alias 2"}]},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.put(
            f"{api_prefix}/entities/items/Q70017/aliases/en",
            json=["New Alias 1", "New Alias 2"],
            headers={"X-Edit-Summary": "replace aliases", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        aliases = data["data"]["aliases"]["en"]
        assert len(aliases) == 2
        assert aliases[0]["value"] == "New Alias 1"
        assert aliases[1]["value"] == "New Alias 2"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_aliases_add(api_prefix: str) -> None:
    """Test updating item aliases creates new if not exists."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70018",
        type="item",
        labels={"en": {"value": "Test Item"}},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.put(
            f"{api_prefix}/entities/items/Q70018/aliases/en",
            json=["Alias 1", "Alias 2"],
            headers={"X-Edit-Summary": "add aliases", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "en" in data["data"]["aliases"]
        assert len(data["data"]["aliases"]["en"]) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_item_aliases_clear(api_prefix: str) -> None:
    """Test updating item aliases with empty list clears them."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q70019",
        type="item",
        aliases={"en": [{"value": "Alias 1"}, {"value": "Alias 2"}]},
        edit_summary="test",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data.model_dump(mode="json"),
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.put(
            f"{api_prefix}/entities/items/Q70019/aliases/en",
            json=[],
            headers={"X-Edit-Summary": "clear aliases", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert (
            "en" not in data["data"]["aliases"] or len(data["data"]["aliases"]["en"]) == 0
        )
