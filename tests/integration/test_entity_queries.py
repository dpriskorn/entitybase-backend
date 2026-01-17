import json
import logging
from typing import Any, Dict, cast

import pytest
import requests

from rapidhash import rapidhash


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_query_locked_entities(api_client: requests.Session, base_url: str) -> None:
    """Query should return locked items"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90010",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Locked"}},
    }
    api_client.post(f"{base_url}/entity", json={**entity_data, "is_locked": True})

    response = api_client.get(f"{base_url}/entities?status=locked")
    assert response.status_code == 200
    entities = response.json()
    assert any(e["entity_id"] == "Q90010" for e in entities)

    logger.info("✓ Query locked entities works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
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
    api_client.post(
        f"{base_url}/entity", json={**entity_data, "is_semi_protected": True}
    )

    response = api_client.get(f"{base_url}/entities?status=semi_protected")
    assert response.status_code == 200
    entities = response.json()
    assert any(e["entity_id"] == "Q90011" for e in entities)

    logger.info("✓ Query semi-protected entities works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_query_archived_entities(api_client: requests.Session, base_url: str) -> None:
    """Query should return archived items"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90012",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Archived"}},
    }
    api_client.post(f"{base_url}/entity", json={**entity_data, "is_archived": True})

    response = api_client.get(f"{base_url}/entities?status=archived")
    assert response.status_code == 200
    entities = response.json()
    assert any(e["entity_id"] == "Q90012" for e in entities)

    logger.info("✓ Query archived entities works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_query_dangling_entities(api_client: requests.Session, base_url: str) -> None:
    """Query should return dangling items"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90013",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Dangling"}},
    }
    api_client.post(f"{base_url}/entity", json={**entity_data, "is_dangling": True})

    response = api_client.get(f"{base_url}/entities?status=dangling")
    assert response.status_code == 200
    entities = response.json()
    assert any(e["entity_id"] == "Q90013" for e in entities)

    logger.info("✓ Query dangling entities works")


def test_list_entities_by_type(api_client: requests.Session, base_url: str) -> None:
    """Test listing entities by type"""
    logger = logging.getLogger(__name__)

    # Create some test entities
    api_client.post(
        f"{base_url}/entitybase/v1/entities/items",
        json={
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Test Item"}},
        },
    )
    api_client.post(
        f"{base_url}/entitybase/v1/entities/lexemes",
        json={
            "type": "lexeme",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "lexicalCategory": "Q1084",
            "language": "Q1860",
        },
    )

    # List items
    response = api_client.get(f"{base_url}/entitybase/v1/entities?entity_type=item")
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
    response = api_client.get(f"{base_url}/entitybase/v1/entities?entity_type=lexeme")
    assert response.status_code == 200
    result = response.json()
    assert result["count"] > 0
    for entity in result["entities"]:
        assert entity["id"].startswith("L")

    logger.info("✓ List entities by type works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_query_by_edit_type(api_client: requests.Session, base_url: str) -> None:
    """Query should return entities filtered by edit_type"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90014",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    api_client.post(
        f"{base_url}/entity",
        json={**entity_data, "is_locked": True, "edit_type": "lock-added"},
    )

    response = api_client.get(f"{base_url}/entities?edit_type=lock-added")
    assert response.status_code == 200
    entities = response.json()
    assert any(e["entity_id"] == "Q90014" for e in entities)

    logger.info("✓ Query by edit_type works")