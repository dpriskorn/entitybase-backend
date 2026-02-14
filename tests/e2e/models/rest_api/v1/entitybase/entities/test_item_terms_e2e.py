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


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_item_add_label_via_post(api_prefix: str) -> None:
    """E2E test: Add new label to item via POST endpoint."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "English Label"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        response = await client.post(
            f"{api_prefix}/entities/{entity_id}/labels/de",
            json={"language": "de", "value": "German Label"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/{entity_id}/labels/de")
        assert response.status_code == 200
        label_data = response.json()
        assert label_data["value"] == "German Label"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_item_add_description_via_post(api_prefix: str) -> None:
    """E2E test: Add new description to item via POST endpoint."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_data = {
            "type": "item",
            "descriptions": {"en": {"language": "en", "value": "English Description"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        response = await client.post(
            f"{api_prefix}/entities/{entity_id}/descriptions/fr",
            json={"language": "fr", "value": "French Description"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(
            f"{api_prefix}/entities/{entity_id}/descriptions/fr"
        )
        assert response.status_code == 200
        description_data = response.json()
        assert description_data["value"] == "French Description"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_item_add_single_alias_via_post(api_prefix: str) -> None:
    """E2E test: Add single alias to item via POST endpoint."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Test Item"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        response = await client.post(
            f"{api_prefix}/entities/{entity_id}/aliases/en",
            json={"language": "en", "value": "New Alias"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/{entity_id}/aliases/en")
        assert response.status_code == 200
        aliases_data = response.json()
        assert "New Alias" in aliases_data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_item_delete_aliases(api_prefix: str) -> None:
    """E2E test: Delete all aliases for a language."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_data = {
            "type": "item",
            "aliases": {
                "en": [
                    {"language": "en", "value": "Alias 1"},
                    {"language": "en", "value": "Alias 2"},
                ],
                "de": [{"language": "de", "value": "Alias DE"}],
            },
        }
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=create_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        response = await client.delete(
            f"{api_prefix}/entities/{entity_id}/aliases/en",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/{entity_id}/aliases/de")
        assert response.status_code == 200
        aliases_data = response.json()
        assert "Alias DE" in aliases_data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_item_term_operations_cross_entity(api_prefix: str) -> None:
    """E2E test: Verify term operations work correctly across multiple entities."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        entity_ids = []
        for i in range(3):
            create_data = {
                "type": "item",
                "labels": {"en": {"language": "en", "value": f"Item {i}"}},
            }
            response = await client.post(
                f"{api_prefix}/entities/items",
                json=create_data,
                headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
            )
            assert response.status_code == 200
            entity_ids.append(response.json()["id"])

        for i, entity_id in enumerate(entity_ids):
            response = await client.get(f"{api_prefix}/entities/{entity_id}/labels/en")
            assert response.status_code == 200
            label_data = response.json()
            assert label_data["value"] == f"Item {i}"
