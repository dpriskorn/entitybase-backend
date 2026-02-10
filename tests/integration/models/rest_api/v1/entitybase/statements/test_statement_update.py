import logging
import sys

sys.path.insert(0, "src")
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient

from models.data.rest_api.v1.entitybase.request import EntityCreateRequest

logger = logging.getLogger(__name__)


from models.rest_api.main import app


@pytest.mark.integration
async def test_delete_statement_success() -> None:
    """Test deleting a statement by hash from an entity."""
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

    response = await client.post(/v1/entitybase/entities/items", json=entity_data, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})
    assert response.status_code == 200

    entity_response = await client.get(/v1/entitybase/entities/Q72001")
    assert entity_response.status_code == 200
    entity = entity_response.json()
    assert "statements" in entity
    assert len(entity["statements"]) == 1

    statement_hash = str(entity["statements"][0])

    delete_response = await client.delete(
        /v1/entitybase/entities/Q72001/statements/{statement_hash}",
        json={},
        headers={"X-Edit-Summary": "delete statement", "X-User-ID": "0"},
    )
    assert delete_response.status_code == 200

    entity_response = await client.get(/v1/entitybase/entities/Q72001")
    assert entity_response.status_code == 200
    entity = entity_response.json()
    assert len(entity["statements"]) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_statement_not_found() -> None:
    """Test deleting a non-existent statement hash returns 404."""
    entity_data = EntityCreateRequest(
        id="Q72002",
        type="item",
        labels={"en": {"value": "Test Entity"}},
        edit_summary="test",
    )

    response = await client.post(
        /v1/entitybase/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    delete_response = await client.delete(
        /v1/entitybase/entities/Q72002/statements/999999",
        json={},
        headers={"X-Edit-Summary": "delete statement", "X-User-ID": "0"},
    )
    assert delete_response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_statement_updates_entity() -> None:
    """Test that deleting a statement increments entity revision."""
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

    response = await client.post(/v1/entitybase/entities/items", json=entity_data, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})
    assert response.status_code == 200

    entity_response = await client.get(/v1/entitybase/entities/Q72003")
    assert entity_response.status_code == 200
    entity = entity_response.json()
    assert entity["rev_id"] == 1

    statement_hash = str(entity["statements"][0])

    delete_response = await client.delete(
        /v1/entitybase/entities/Q72003/statements/{statement_hash}",
        json={},
        headers={"X-Edit-Summary": "delete statement", "X-User-ID": "0"},
    )
    assert delete_response.status_code == 200

    entity_response = await client.get(/v1/entitybase/entities/Q72003")
    assert entity_response.status_code == 200
    entity = entity_response.json()
    assert entity["rev_id"] == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_patch_statement_success() -> None:
    """Test patching a statement by hash with new claim data."""
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

    response = await client.post(/v1/entitybase/entities/items", json=entity_data, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})
    assert response.status_code == 200

    entity_response = await client.get(/v1/entitybase/entities/Q72004")
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
        /v1/entitybase/entities/Q72004/statements/{statement_hash}",
        json=patch_data,
        headers={"X-Edit-Summary": "patch statement", "X-User-ID": "0"},
    )
    assert patch_response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.integration
async def test_patch_statement_not_found() -> None:
    """Test patching a non-existent statement hash returns 404."""
    entity_data = EntityCreateRequest(
        id="Q72005",
        type="item",
        labels={"en": {"value": "Test Entity"}},
        edit_summary="test",
    )

    response = await client.post(
        /v1/entitybase/entities/items",
        json=entity_data.model_dump(mode="json"),
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 200

    patch_data = {
        "claims": {}
    }

    patch_response = await client.patch(
        /v1/entitybase/entities/Q72005/statements/999999",
        json=patch_data,
        headers={"X-Edit-Summary": "patch statement", "X-User-ID": "0"},
    )
    assert patch_response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_patch_statement_modifies_value() -> None:
    """Test that patching a statement modifies the value correctly."""
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

    response = await client.post(/v1/entitybase/entities/items", json=entity_data, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})
    assert response.status_code == 200

    entity_response = await client.get(/v1/entitybase/entities/Q72006")
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
        /v1/entitybase/entities/Q72006/statements/{statement_hash}",
        json=patch_data,
        headers={"X-Edit-Summary": "patch statement", "X-User-ID": "0"},
    )
    assert patch_response.status_code == 200

    entity_response = await client.get(/v1/entitybase/entities/Q72006")
    assert entity_response.status_code == 200
    entity = entity_response.json()
    assert entity["rev_id"] == 2
