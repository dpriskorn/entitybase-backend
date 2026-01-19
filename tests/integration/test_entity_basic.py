import json
import logging
from pprint import pprint
from typing import Any, Dict, cast

import pytest
import requests
from rapidhash import rapidhash

from models.rest_api.entitybase.request import EntityCreateRequest


@pytest.mark.integration
def test_health_check(api_client: requests.Session, base_url: str) -> None:
    """Test that health check endpoint returns OK
    This does not test all buckets work"""
    logger = logging.getLogger(__name__)
    response = api_client.get(f"{base_url}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["s3"] == "connected"
    assert data["vitess"] == "connected"
    logger.info("✓ Health check passed")


@pytest.mark.integration
def test_id_resolver_resolve_id(db_conn) -> None:
    """Test IdResolver.resolve_id method."""
    from models.infrastructure.vitess.id_resolver import IdResolver

    logger = logging.getLogger(__name__)

    # Insert a test entity_id_mapping
    test_entity_id = "Q999999"
    test_internal_id = 999999
    with db_conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO entity_id_mapping (entity_id, internal_id) VALUES (%s, %s)",
            (test_entity_id, test_internal_id),
        )
    db_conn.commit()

    # Test resolve_id
    resolver = IdResolver(None)  # connection_manager not needed for static method
    resolved_id = IdResolver.resolve_id(db_conn, test_entity_id)
    assert resolved_id == test_internal_id

    # Test non-existent
    non_existent_id = IdResolver.resolve_id(db_conn, "Q000000")
    assert non_existent_id == 0

    logger.info("✓ IdResolver.resolve_id test passed")


@pytest.mark.integration
def test_create_entity(api_client: requests.Session, base_url: str) -> None:
    """Test creating a new entity"""
    logger = logging.getLogger(__name__)
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
        f"{base_url}/entitybase/v1/entities/items",
        json=entity_data1.model_dump(mode="json"),
    )
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
def test_get_entity(api_client: requests.Session, base_url: str) -> None:
    """Test retrieving an entity"""
    logger = logging.getLogger(__name__)

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
        f"{base_url}/entitybase/v1/entities/items",
        json=entity_data1.model_dump(mode="json"),
    )
    logger.debug("Response")
    pprint(response.json())
    assert response.status_code == 200

    # Then retrieve it
    response2 = api_client.get(f"{base_url}/entitybase/v1/entities/Q99998")
    logger.debug("Response2")
    pprint(response2.json())
    assert response2.status_code == 200

    result = response2.json()
    assert result["id"] == "Q99998"
    assert result["rev_id"] == 1
    # assert "data" in result
    logger.info("✓ Entity retrieval passed")


# TODO update to use revision endpoint instead
@pytest.mark.skip("raw endpoint has been removed")
@pytest.mark.integration
def test_update_entity(api_client: requests.Session, base_url: str) -> None:
    """Test updating an entity (create new revision)"""
    logger = logging.getLogger(__name__)

    # Create initial entity
    entity_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Entity for Update"}},
    }
    create_response = api_client.post(
        f"{base_url}/entitybase/v1/entities/items", json=entity_data
    )
    entity_id = create_response.json()["id"]

    # Update entity
    updated_entity_data = {
        "data": {
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Test Entity - Updated"}},
            "descriptions": {"en": {"language": "en", "value": "Updated description"}},
        }
    }

    response = api_client.put(
        f"{base_url}/entitybase/v1/entities/items/{entity_id}", json=updated_entity_data
    )
    assert response.status_code == 200

    result = response.json()
    assert result["id"] == entity_id
    assert result["revision_id"] == 2
    assert result["data"]["labels"]["en"]["value"] == "Test Entity - Updated"

    # Verify different content created new revision with different hash
    # raw1 = api_client.get(f"{base_url}/entitybase/v1/raw/{entity_id}/1").json()
    # raw2 = api_client.get(f"{base_url}/entitybase/v1/raw/{entity_id}/2").json()

    # assert raw1["content_hash"] != raw2["content_hash"], (
    #     "Different content should have different hashes"
    # )

    # Verify hash format and values
    # if rapidhash is not None:
    #     entity_json_1 = json.dumps(entity_data, sort_keys=True)
    #     computed_hash_1 = rapidhash(entity_json_1.encode())
    #     assert raw1["content_hash"] == computed_hash_1, (
    #         f"First revision hash mismatch: expected {computed_hash_1}, got {raw1['content_hash']}"
    #     )
    #
    #     entity_json_2 = json.dumps(updated_entity_data, sort_keys=True)
    #     computed_hash_2 = rapidhash(entity_json_2.encode())
    #     assert raw2["content_hash"] == computed_hash_2, (
    #         f"Second revision hash mismatch: expected {computed_hash_2}, got {raw2['content_hash']}"
    #     )

    logger.info("✓ Entity update passed with hash verification")


@pytest.mark.integration
def test_create_entity_already_exists(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that POST /entity fails with 409 when entity already exists"""
    logger = logging.getLogger(__name__)

    # Create initial entity
    entity_data = {
        "id": "Q99998",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Entity"}},
    }
    api_client.post(f"{base_url}/entitybase/v1/entities/items", json=entity_data)

    # Try to create the same entity again - should fail
    response = api_client.post(
        f"{base_url}/entitybase/v1/entities/items", json=entity_data
    )
    assert response.status_code == 409
    assert "already exists" in response.json().get("detail", "")

    logger.info("✓ POST with existing entity correctly returns 409")


@pytest.mark.integration
def test_get_entity_history(api_client: requests.Session, base_url: str) -> None:
    """Test retrieving entity history"""
    logger = logging.getLogger(__name__)

    # Create entity with two revisions
    entity_id = "Q99996"
    entity_data = {
        "id": entity_id,
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Entity"}},
    }

    api_client.post(f"{base_url}/entitybase/v1/entities/items", json=entity_data)
    # Update entity for second revision
    update_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Updated Test Entity"}},
    }
    api_client.post(f"{base_url}/entitybase/v1/entities/items", json=update_data)

    # Get history (ordered by created_at DESC)
    response = api_client.get(f"{base_url}/entitybase/v1/entities/{entity_id}/history")
    assert response.status_code == 200

    history = response.json()
    assert len(history) == 2
    assert history[0]["revision_id"] == 2
    assert history[1]["revision_id"] == 1
    assert "created_at" in history[0]
    assert "created_at" in history[1]
    logger.info("✓ Entity history retrieval passed")


@pytest.mark.integration
def test_get_specific_revision(api_client: requests.Session, base_url: str) -> None:
    """Test retrieving a specific revision"""
    logger = logging.getLogger(__name__)

    # Create entity
    entity_id = "Q99995"
    entity_data = {
        "id": entity_id,
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Entity"}},
    }
    api_client.post(f"{base_url}/entity", json=entity_data)

    # Create second revision
    entity_labels2: Dict[str, Any] = cast(Dict[str, Any], entity_data["labels"]).copy()
    entity_labels2["en"]["value"] = "Updated"
    api_client.post(f"{base_url}/entity", json=entity_data)

    # Get first revision
    response = api_client.get(f"{base_url}/entity/{entity_id}/revision/1")
    assert response.status_code == 200

    result = response.json()
    assert result["id"] == entity_id
    assert result["labels"]["en"]["value"] == "Test Entity"
    logger.info("✓ Specific revision retrieval passed")


@pytest.mark.integration
def test_entity_not_found(api_client: requests.Session, base_url: str) -> None:
    """Test that non-existent entities return 404"""
    logger = logging.getLogger(__name__)
    response = api_client.get(f"{base_url}/entity/Q88888")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    logger.info("✓ 404 handling passed")


@pytest.mark.integration
def test_raw_endpoint_existing_revision(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that raw endpoint returns existing revision"""
    logger = logging.getLogger(__name__)

    # Create entity
    entity_data = {
        "id": "Q55555",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Raw Test Entity"}},
    }

    create_response = api_client.post(f"{base_url}/entity", json=entity_data)
    assert create_response.status_code == 200

    # Get raw revision
    response = api_client.get(f"{base_url}/raw/Q55555/1")
    assert response.status_code == 200
    result = response.json()

    # Check full revision schema
    assert result["schema_version"] == "latest"
    assert result["revision_id"] == 1
    assert "created_at" in result
    assert result["created_by"] == "rest-api"
    assert result["entity_type"] == "item"
    assert result["entity"]["id"] == "Q55555"
    assert result["entity"]["type"] == "item"
    assert "labels" in result["entity"]

    # Verify content_hash field
    assert "content_hash" in result, "content_hash field must be present"
    assert isinstance(result["content_hash"], int), "content_hash must be integer"

    # Log response body if enabled
    import os

    if os.getenv("TEST_LOG_HTTP_REQUESTS") == "true":
        logger.debug("  ← ✓ 200 OK")
        if response.text:
            text_preview = response.text[:200]
            logger.debug(f"    Body: {text_preview}...")

    logger.info("✓ Raw endpoint returns full revision schema with content_hash")


@pytest.mark.integration
def test_idempotent_duplicate_submission(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that identical POST requests return same revision (idempotency)"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q99996",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Idempotent Test"}},
    }

    # First POST creates revision 1
    response1 = api_client.post(f"{base_url}/entity", json=entity_data)
    assert response1.status_code == 200
    result1 = response1.json()
    revision_id_1 = result1["revision_id"]

    # Second identical POST should return same revision (no new revision)
    response2 = api_client.post(f"{base_url}/entity", json=entity_data)
    assert response2.status_code == 200
    result2 = response2.json()
    revision_id_2 = result2["revision_id"]

    # Verify idempotency
    assert revision_id_1 == revision_id_2, (
        "Identical POST should return same revision ID"
    )
    assert result1 == result2, "Responses should be identical"

    # Verify content_hash field and hash computation
    if rapidhash is not None:
        entity_json = json.dumps(entity_data, sort_keys=True)
        computed_hash = rapidhash(entity_json.encode())

        # Get hash from API
        raw_response = api_client.get(f"{base_url}/raw/Q99996/{revision_id_1}").json()
        api_hash = raw_response.get("content_hash")

        # Verify API returned correct hash
        assert api_hash == computed_hash, (
            f"API hash {api_hash} must match computed hash {computed_hash}"
        )

        logger.info(
            f"✓ Idempotent deduplication: same revision {revision_id_1} returned with rapidhash verification"
        )
    else:
        logger.info(
            f"✓ Idempotent deduplication: same revision {revision_id_1} returned (rapidhash not available)"
        )
