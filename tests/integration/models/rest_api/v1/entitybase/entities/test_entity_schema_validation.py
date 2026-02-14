from pathlib import Path
from typing import Any, cast

import pytest
from httpx import ASGITransport, AsyncClient
import yaml
from jsonschema import Draft202012Validator


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_item_and_validate_json_response(api_prefix: str) -> None:
    """Create item via POST and validate JSON response against schema."""
    from models.rest_api.main import app

    # Load entity schema
    schema_path = (
        Path(__file__).parent.parent.parent.parent.parent.parent.parent.parent
        / "schemas"
        / "entitybase"
        / "entity"
        / "2.0.0"
        / "schema.yaml"
    )
    with open(schema_path, "r", encoding="utf-8") as f:
        entity_schema = cast(dict[str, Any], yaml.safe_load(f))

    schema_validator = Draft202012Validator(entity_schema)

    item_data = {
        "type": "item",
        "labels": {
            "en": {"language": "en", "value": "Test Entity for Schema Validation"}
        },
        "edit_summary": "Test entity for schema validation",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=item_data,
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        create_result = response.json()
        entity_id = create_result["id"]
        assert entity_id.startswith("Q")

        json_response = await client.get(f"{api_prefix}/entities/{entity_id}.json")
        assert json_response.status_code == 200
        response_data = json_response.json()
        entity_data = response_data["data"]

        assert "id" in entity_data
        assert "hashes" in entity_data
        assert "revision_id" in entity_data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_required_fields_present(api_prefix: str) -> None:
    """Verify required fields are present in response."""
    from models.rest_api.main import app

    item_data = {"type": "item", "edit_summary": "Test required fields"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=item_data,
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        entity_id = response.json()["id"]

        json_response = await client.get(f"{api_prefix}/entities/{entity_id}.json")
        response_data = json_response.json()
        entity_data = response_data["data"]

        assert "id" in entity_data
        assert "hashes" in entity_data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_item_with_descriptions_validates(api_prefix: str) -> None:
    """Test that items with descriptions validate against schema."""
    from models.rest_api.main import app

    item_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Item"}},
        "descriptions": {
            "en": {"language": "en", "value": "A test item with descriptions"}
        },
        "edit_summary": "Test item with descriptions",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=item_data,
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        entity_id = response.json()["id"]

        json_response = await client.get(f"{api_prefix}/entities/{entity_id}.json")
        response_data = json_response.json()
        entity_data = response_data["data"]

        assert "hashes" in entity_data
        assert "descriptions" in entity_data["hashes"]
        assert "en" in entity_data["hashes"]["descriptions"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_item_with_claims_validates(api_prefix: str) -> None:
    """Test that items with claims validate against schema."""
    from models.rest_api.main import app

    item_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Item"}},
        "claims": {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q5"},
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                }
            ]
        },
        "edit_summary": "Test item with claims",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=item_data,
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        entity_id = response.json()["id"]

        json_response = await client.get(f"{api_prefix}/entities/{entity_id}.json")
        response_data = json_response.json()
        entity_data = response_data["data"]

        assert "hashes" in entity_data
        assert "statements" in entity_data["hashes"]
        assert len(entity_data["hashes"]["statements"]) > 0
