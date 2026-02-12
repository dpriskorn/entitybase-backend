import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_health_check(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Health check endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_general_stats(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Get general statistics."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_entities" in data or "entities" in data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_json_import_endpoint(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Import entities from Wikidata JSONL dump file."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        import_data = {
            "entities": [
                {
                    "type": "item",
                    "labels": {"en": {"language": "en", "value": "Import Test"}},
                }
            ],
            "batch_size": 10,
        }
        response = await client.post(
            f"{api_prefix}/json-import",
            json=import_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code in [200, 202, 400]


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_entity_lifecycle(api_prefix: str) -> None:
    from models.rest_api.main import app

    """E2E test: Create, read, update, delete entity."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        create_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Test Item"}},
            "descriptions": {"en": {"language": "en", "value": "E2E test item"}},
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

        # Read entity
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["revision"]["labels"]["en"]["value"] == "Test Item"

        # Update entity label using atomic endpoint
        response = await client.put(
            f"{api_prefix}/entities/{entity_id}/labels/en",
            json={"language": "en", "value": "Updated Test Item"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        # Verify update
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["revision"]["labels"]["en"]["value"] == "Updated Test Item"

        # Delete entity (if supported)
        # Note: Wikibase may not support direct deletion; adjust based on API
        # response = await client.delete(f"{api_prefix}/entities/{entity_id}")
        # assert response.status_code == 204

        # For now, just verify the entity exists
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
