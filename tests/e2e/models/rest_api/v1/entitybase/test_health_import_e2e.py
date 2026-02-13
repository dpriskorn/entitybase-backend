"""E2E tests for health check and import endpoints."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_health_check() -> None:
    """E2E test: Health check endpoint for monitoring service status."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data or data.get("healthy") is not None


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_import_single_entity() -> None:
    """E2E test: Import a single entity of any type."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Import an item
        entity_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Imported Item"}},
            "descriptions": {"en": {"language": "en", "value": "Imported via API"}},
        }
        response = await client.post(
            "/import",
            json=entity_data,
            headers={"X-Edit-Summary": "Import E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["id"].startswith("Q")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_import_property() -> None:
    """E2E test: Import a property entity."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Import a property
        property_data = {
            "type": "property",
            "datatype": "string",
            "labels": {"en": {"language": "en", "value": "Imported Property"}},
            "descriptions": {"en": {"language": "en", "value": "Imported property"}},
        }
        response = await client.post(
            "/import",
            json=property_data,
            headers={"X-Edit-Summary": "Import E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["id"].startswith("P")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_import_lexeme() -> None:
    """E2E test: Import a lexeme entity."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Import a lexeme
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "import"}},
            "labels": {"en": {"language": "en", "value": "imported lexeme"}},
        }
        response = await client.post(
            "/import",
            json=lexeme_data,
            headers={"X-Edit-Summary": "Import E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["id"].startswith("L")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_import_entity_with_statements() -> None:
    """E2E test: Import an entity with statements."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Import an item with statements
        entity_data = {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Item with Statements"}},
            "statements": [
                {
                    "property": {"id": "P31", "data_type": "wikibase-item"},
                    "value": {"type": "value", "content": "Q5"},
                    "rank": "normal",
                }
            ],
        }
        response = await client.post(
            "/import",
            json=entity_data,
            headers={"X-Edit-Summary": "Import E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_import_validation_error() -> None:
    """E2E test: Import fails for invalid entity data."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Try to import invalid entity (missing type)
        entity_data = {
            "labels": {"en": {"language": "en", "value": "Invalid"}},
        }
        response = await client.post(
            "/import",
            json=entity_data,
            headers={"X-Edit-Summary": "Import E2E test", "X-User-ID": "0"},
        )
        assert response.status_code in [400, 422]
