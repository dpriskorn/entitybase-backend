import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
@pytest.mark.integration
def test_query_locked_entities(api_client: requests.Session, base_url: str) -> None:
    """Query should return locked items"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90010",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Locked"}},
    }
    await client.post("/v1/entitybase/entities/", json={**entity_data, "is_locked": True}, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})

    response = await client.get(f"{base_url}/entities?status=locked")
    assert response.status_code == 200
    entities = response.json()
    assert any(e["entity_id"] == "Q90010" for e in entities)

    logger.info("✓ Query locked entities works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
@pytest.mark.integration
def test_query_semi_protected_entities(
    api_client: requests.Session, base_url: str
) -> None:
    """Query should return semi-protected items"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90011",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Protected"}},
    }
    await client.post(
        "/v1/entitybase/entities/", json={**entity_data, "is_semi_protected": True}, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"}
    )

    response = await client.get(f"{base_url}/entities?status=semi_protected")
    assert response.status_code == 200
    entities = response.json()
    assert any(e["entity_id"] == "Q90011" for e in entities)

    logger.info("✓ Query semi-protected entities works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
@pytest.mark.integration
def test_query_archived_entities(api_client: requests.Session, base_url: str) -> None:
    """Query should return archived items"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90012",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Archived"}},
    }
    await client.post("/v1/entitybase/entities/", json={**entity_data, "is_archived": True}, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})

    response = await client.get(f"{base_url}/entities?status=archived")
    assert response.status_code == 200
    entities = response.json()
    assert any(e["entity_id"] == "Q90012" for e in entities)

    logger.info("✓ Query archived entities works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
@pytest.mark.integration
def test_query_dangling_entities(api_client: requests.Session, base_url: str) -> None:
    """Query should return dangling items"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90013",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Dangling"}},
    }
    await client.post("/v1/entitybase/entities/", json={**entity_data, "is_dangling": True}, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})

    response = await client.get(f"{base_url}/entities?status=dangling")
    assert response.status_code == 200
    entities = response.json()
    assert any(e["entity_id"] == "Q90013" for e in entities)

    logger.info("✓ Query dangling entities works")


@pytest.mark.integration
def test_list_entities_by_type(api_client: requests.Session, base_url: str) -> None:
    """Test listing entities by type"""
    logger = logging.getLogger(__name__)

    # Create some test entities
    await client.post(
        "/v1/entitybase/entities/base/v1/entities/items",
        json={
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Test Item"}},
        },
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    await client.post(
        "/v1/entitybase/entities/base/v1/entities/lexemes",
        json={
            "type": "lexeme",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "lexicalCategory": "Q1084",
            "language": "Q1860",
        },
        headers={"X-Edit-Summary": "create lexeme", "X-User-ID": "0"},
    )

    # List items
    response = await client.get("/v1/entitybase/entities/base/v1/entities?entity_type=item")
    assert response.status_code == 200
    result = response.json()
    assert "entities" in result
    assert "count" in result
    assert result["count"] > 0
    for entity in result["entities"]:
        assert "id" in entity
        assert "revision_id" in entity
        assert entity["id"].startswith("Q")

    # List lexemes
    response = await client.get("/v1/entitybase/entities/base/v1/entities?entity_type=lexeme")
    assert response.status_code == 200
    result = response.json()
    assert result["count"] > 0
    for entity in result["entities"]:
        assert entity["id"].startswith("L")

    logger.info("✓ List entities by type works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
@pytest.mark.integration
def test_query_by_edit_type(api_client: requests.Session, base_url: str) -> None:
    """Query should return entities filtered by edit_type"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90014",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    await client.post(
        "/v1/entitybase/entities/",
        json={**entity_data, "is_locked": True, "edit_type": "lock-added"},
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )

    response = await client.get(f"{base_url}/entities?edit_type=lock-added")
    assert response.status_code == 200
    entities = response.json()
    assert any(e["entity_id"] == "Q90014" for e in entities)

    logger.info("✓ Query by edit_type works")
