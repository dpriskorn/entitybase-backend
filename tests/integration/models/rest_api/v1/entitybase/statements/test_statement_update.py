import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient

from models.data.rest_api.v1.entitybase.request import EntityCreateRequest

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_statement_success(api_prefix: str) -> None:
    """Test deleting a statement by hash from an entity."""
    from models.rest_api.main import app

    entity_data = {
        "id": "Q72001",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Entity"}},
        "claims": {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datatype": "wikibase-item",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q5"},
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                }
            ]
        },
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(f"{api_prefix}/entities/items", json=entity_data, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})
        assert response.status_code == 200

        entity_response = await client.get(f"{api_prefix}/entities/Q72001")
        assert entity_response.status_code == 200
        entity = entity_response.json()
        assert "statements" in entity
        assert len(entity["statements"]) == 1

        statement_hash = str(entity["statements"][0])

        delete_response = await client.delete(
            f"{api_prefix}/entities/Q72001/statements/" + statement_hash,
            json={},
            headers={"X-Edit-Summary": "delete statement", "X-User-ID": "0"},
        )
        assert delete_response.status_code == 200

        entity_response = await client.get(f"{api_prefix}/entities/Q72001")
        assert entity_response.status_code == 200
        entity = entity_response.json()
        assert len(entity["statements"]) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_statement_not_found(api_prefix: str) -> None:
    """Test deleting a non-existent statement hash returns 404."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q72002",
        type="item",
        labels={"en": {"value": "Test Entity"}},
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

        delete_response = await client.delete(
            f"{api_prefix}/entities/Q72002/statements/999999",
            json={},
            headers={"X-Edit-Summary": "delete statement", "X-User-ID": "0"},
        )
        assert delete_response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_statement_updates_entity(api_prefix: str) -> None:
    """Test that deleting a statement increments entity revision."""
    from models.rest_api.main import app

    entity_data = {
        "id": "Q72003",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Entity"}},
        "claims": {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datatype": "wikibase-item",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q5"},
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                }
            ]
        },
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(f"{api_prefix}/entities/items", json=entity_data, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})
        assert response.status_code == 200

        entity_response = await client.get(f"{api_prefix}/entities/Q72003")
        assert entity_response.status_code == 200
        entity = entity_response.json()
        assert entity["rev_id"] == 1

        statement_hash = str(entity["statements"][0])

        delete_response = await client.delete(
            f"{api_prefix}/entities/Q72003/statements/" + statement_hash,
            json={},
            headers={"X-Edit-Summary": "delete statement", "X-User-ID": "0"},
        )
        assert delete_response.status_code == 200

        entity_response = await client.get(f"{api_prefix}/entities/Q72003")
        assert entity_response.status_code == 200
        entity = entity_response.json()
        assert entity["rev_id"] == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_patch_statement_success(api_prefix: str) -> None:
    """Test patching a statement by hash with new claim data."""
    from models.rest_api.main import app

    entity_data = {
        "id": "Q72004",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Entity"}},
        "claims": {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datatype": "wikibase-item",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q5"},
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                }
            ]
        },
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(f"{api_prefix}/entities/items", json=entity_data, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})
        assert response.status_code == 200

        entity_response = await client.get(f"{api_prefix}/entities/Q72004")
        assert entity_response.status_code == 200
        entity = entity_response.json()
        statement_hash = str(entity["statements"][0])

        patch_data = {
            "claims": {
                "P31": [
                    {
                        "mainsnak": {
                            "snaktype": "value",
                            "property": "P31",
                            "datatype": "wikibase-item",
                            "datavalue": {
                                "value": {"entity-type": "item", "id": "Q515"},
                                "type": "wikibase-entityid",
                            },
                        },
                        "type": "statement",
                        "rank": "normal",
                        "qualifiers": {},
                        "references": [],
                    }
                ]
            }
        }

        patch_response = await client.patch(
            f"{api_prefix}/entities/Q72004/statements/" + statement_hash,
            json=patch_data,
            headers={"X-Edit-Summary": "patch statement", "X-User-ID": "0"},
        )
        assert patch_response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.integration
async def test_patch_statement_not_found(api_prefix: str) -> None:
    """Test patching a non-existent statement hash returns 404."""
    from models.rest_api.main import app

    entity_data = EntityCreateRequest(
        id="Q72005",
        type="item",
        labels={"en": {"value": "Test Entity"}},
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

        patch_data = {
            "claims": {}
        }

        patch_response = await client.patch(
            f"{api_prefix}/entities/Q72005/statements/999999",
            json=patch_data,
            headers={"X-Edit-Summary": "patch statement", "X-User-ID": "0"},
        )
        assert patch_response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_patch_statement_modifies_value(api_prefix: str) -> None:
    """Test that patching a statement modifies the value correctly."""
    from models.rest_api.main import app

    entity_data = {
        "id": "Q72006",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Entity"}},
        "claims": {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datatype": "wikibase-item",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q5"},
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                }
            ]
        },
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(f"{api_prefix}/entities/items", json=entity_data, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})
        assert response.status_code == 200

        entity_response = await client.get(f"{api_prefix}/entities/Q72006")
        assert entity_response.status_code == 200
        entity = entity_response.json()
        statement_hash = str(entity["statements"][0])

        patch_data = {
            "claims": {
                "P31": [
                    {
                        "mainsnak": {
                            "snaktype": "value",
                            "property": "P31",
                            "datatype": "wikibase-item",
                            "datavalue": {
                                "value": {"entity-type": "item", "id": "Q515"},
                                "type": "wikibase-entityid",
                            },
                        },
                        "type": "statement",
                        "rank": "preferred",
                        "qualifiers": {},
                        "references": [],
                    }
                ]
            }
        }

        patch_response = await client.patch(
            f"{api_prefix}/entities/Q72006/statements/" + statement_hash,
            json=patch_data,
            headers={"X-Edit-Summary": "patch statement", "X-User-ID": "0"},
        )
        assert patch_response.status_code == 200

        entity_response = await client.get(f"{api_prefix}/entities/Q72006")
        assert entity_response.status_code == 200
        entity = entity_response.json()
        assert entity["rev_id"] == 2
