import json
import logging
from pprint import pprint

import pytest
import requests
from rapidhash import rapidhash

from models.data.rest_api.v1.entitybase.request import EntityCreateRequest

logger = logging.getLogger(__name__)


@pytest.mark.integration
def test_health_check(api_client: requests.Session, base_url: str) -> None:
    """Test that health check endpoint returns OK
    This does not test all buckets work"""

    response = api_client.get(f"{base_url}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["s3"] == "connected"
    assert data["vitess"] == "connected"
    logger.info("✓ Health check passed")


@pytest.mark.integration
def test_create_item(api_client: requests.Session, api_url: str) -> None:
    """Test creating a new entity"""
    entity_data1 = EntityCreateRequest(
        type="item", labels={"en": {"value": "Test Entity"}}, edit_summary="test"
    )
    # entity_data = {
    #     "type": "item",
    #     "labels": {"en": {"language": "en", "value": "Test Entity"}},
    #     "descriptions": {
    #         "en": {"language": "en", "value": "A test entity for integration testing"}
    #     },
    # }

    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data1.model_dump(mode="json"),
    )

    # Debug output for 500 error investigation
    logger.error(f"🔍 TEST: Status Code: {response.status_code}")
    logger.error(f"🔍 TEST: Response Headers: {dict(response.headers)}")
    if response.status_code >= 400:
        logger.error(f"🔍 TEST: Response Body: {response.text}")
        logger.error(f"🔍 TEST: Request Data: {entity_data1.model_dump(mode='json')}")

    assert response.status_code == 200

    result = response.json()
    logger.debug(result)
    entity_id = result["id"]
    assert entity_id.startswith("Q")
    assert result["rev_id"] == 1

    # Hash computation now works with nested data property
    # entity_json = json.dumps(result["data"], sort_keys=True)
    # computed_hash = rapidhash(entity_json.encode())
    #
    # raw_response = api_client.get(f"{base_url}/entitybase/raw/{entity_id}/1")
    # raw_data = raw_response.json()
    # api_hash = raw_data.get("content_hash")
    #
    # assert api_hash == computed_hash, (
    #     f"API hash {api_hash} must match computed hash {computed_hash}"
    # )
    #
    # logger.info("✓ Entity creation passed with rapidhash verification")


@pytest.mark.integration
def test_get_item(api_client: requests.Session, api_url: str) -> None:
    """Test retrieving an entity"""


    # First create an entity
    entity_data1 = EntityCreateRequest(
        id="Q99998",
        type="item",
        labels={"en": {"value": "Test Entity"}},
        edit_summary="test",
    )
    # entity_data = {
    #     "id": "Q99998",
    #     "type": "item",
    #     "labels": {"en": {"language": "en", "value": "Test Entity for Get"}},
    # }
    response = api_client.post(
        f"{api_url}/entities/items",
        json=entity_data1.model_dump(mode="json"),
    )
    logger.debug("Response")
    pprint(response.json())
    assert response.status_code == 200

    # Then retrieve it
    response2 = api_client.get(f"{api_url}/entities/Q99998")
    logger.debug("Response2")
    pprint(response2.json())
    assert response2.status_code == 200

    result = response2.json()
    assert result["id"] == "Q99998"
    assert result["rev_id"] == 1
    # assert "data" in result
    logger.info("✓ Entity retrieval passed")



@pytest.mark.integration
def test_create_item_already_exists(
    api_client: requests.Session, api_url: str
) -> None:
    """Test that POST /entity fails with 409 when entity already exists"""


    # Create initial entity
    entity_data = {
        "id": "Q99998",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Entity"}},
        "edit_summary": "Test creation",
    }
    api_client.post(f"{api_url}/entities/items", json=entity_data)

    # Try to create the same entity again - should fail
    response = api_client.post(
        f"{api_url}/entities/items", json=entity_data
    )
    assert response.status_code == 409
    assert "already exists" in response.json().get("message", "")

    logger.info("✓ POST with existing entity correctly returns 409")


@pytest.mark.integration
def test_get_item_history(api_client: requests.Session, api_url: str) -> None:
    """Test retrieving entity history"""


    # Create entity with two revisions
    entity_id = "Q99996"
    entity_data = {
        "id": entity_id,
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Entity"}},
        "edit_summary": "create entity",
    }

    api_client.post(f"{api_url}/entities/items", json=entity_data)
    # Update entity for second revision
    update_data = {
        "id": entity_id,
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Updated Test Entity"}},
        "edit_summary": "update entity",
    }
    api_client.post(f"{api_url}/entities/items", json=update_data)

    # Get history (ordered by created_at DESC)
    response = api_client.get(f"{api_url}/entities/{entity_id}/history")
    assert response.status_code == 200

    history = response.json()
    assert len(history) == 2
    assert history[0]["revision_id"] == 2
    assert history[1]["revision_id"] == 1
    assert "created_at" in history[0]
    assert "created_at" in history[1]
    logger.info("✓ Entity history retrieval passed")


@pytest.mark.integration
def test_entity_not_found(api_client: requests.Session, api_url: str) -> None:
    """Test that non-existent entities return 404"""

    response = api_client.get(f"{api_url}/entities/Q88888")
    assert response.status_code == 404
    assert "not found" in response.json()["message"].lower()
    logger.info("✓ 404 handling passed")
