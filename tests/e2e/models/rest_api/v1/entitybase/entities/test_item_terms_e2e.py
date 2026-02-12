import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_item_labels_full_workflow(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Create item, update labels, get labels, delete labels."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Initial Label"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_data = response.json()
        entity_id = entity_data["id"]
        assert entity_id.startswith("Q")

        response = await client.get(f"{api_prefix}/entities/{entity_id}/labels/en")
        assert response.status_code == 200
        label_data = response.json()
        assert label_data["value"] == "Initial Label"

        response = await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "Updated Label"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/{entity_id}/labels/en")
        assert response.status_code == 200
        label_data = response.json()
        assert label_data["value"] == "Updated Label"

        response = await client.delete(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_item_descriptions_full_workflow(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Create item, update descriptions, get descriptions, delete descriptions."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_data = {
            "type": "item",
            "descriptions": {"en": {"language": "en", "value": "Initial Description"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_data = response.json()
        entity_id = entity_data["id"]
        assert entity_id.startswith("Q")

        response = await client.get(
            f"{api_prefix}/entities/{entity_id}/descriptions/en"
        )
        assert response.status_code == 200
        description_data = response.json()
        assert description_data["value"] == "Initial Description"

        response = await client.put(
            f"{api_prefix}/entities/{entity_id}/descriptions/en",
            json={"language": "en", "value": "Updated Description"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(
            f"{api_prefix}/entities/{entity_id}/descriptions/en"
        )
        assert response.status_code == 200
        description_data = response.json()
        assert description_data["value"] == "Updated Description"

        response = await client.delete(
            f"{api_prefix}/entities/{entity_id}/descriptions/en",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_item_aliases_full_workflow(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Create item, update aliases, get aliases."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_data = {
            "type": "item",
            "aliases": {"en": [{"language": "en", "value": "Alias 1"}]},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_data = response.json()
        entity_id = entity_data["id"]
        assert entity_id.startswith("Q")

        response = await client.get(f"{api_prefix}/entities/{entity_id}/aliases/en")
        assert response.status_code == 200
        aliases_data = response.json()
        assert len(aliases_data) == 1
        assert "Alias 1" in aliases_data

        response = await client.put(
            f"{api_prefix}/entities/{entity_id}/aliases/en",
            json=["Alias 1", "Alias 2", "Alias 3"],
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/{entity_id}/aliases/en")
        assert response.status_code == 200
        aliases_data = response.json()
        assert len(aliases_data) == 3
