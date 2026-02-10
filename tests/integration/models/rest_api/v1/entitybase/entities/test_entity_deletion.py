import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
def test_hard_delete_entity(api_client: requests.Session, base_url: str) -> None:
    """Test hard deleting an entity"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q99002",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "To Hard Delete"}},
    }

    # Create entity
    await client.post("/v1/entitybase/entities/", json=entity_data, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})

    # Hard delete
    delete_response = await client.delete(
        "/v1/entitybase/entities//Q99002",
        json={"delete_type": "hard"},
        headers={"X-Edit-Summary": "delete entity", "X-User-ID": "0"},
    )
    assert delete_response.status_code == 200

    result = delete_response.json()
    assert result["id"] == "Q99002"
    assert result["is_deleted"] is True
    assert result["deletion_type"] == "hard"

    # Verify entity no longer accessible (hard delete hides)
    get_response = await client.get("/v1/entitybase/entities//Q99002")
    assert get_response.status_code == 410  # Gone
    assert "deleted" in get_response.json()["message"].lower()

    logger.info("✓ Hard delete hides entity correctly")


@pytest.mark.integration
def test_hard_delete_prevents_undelete(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that hard deleted entities cannot be undeleted"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q99004",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "To Hard Delete"}},
    }

    # Create entity
    await client.post("/v1/entitybase/entities/", json=entity_data, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})

    # Hard delete
    await client.delete(
        "/v1/entitybase/entities//Q99004",
        json={"delete_type": "hard"},
        headers={"X-Edit-Summary": "delete entity", "X-User-ID": "0"},
    )

    # Try to undelete (should fail with 410)
    response = await client.post(
        "/v1/entitybase/entities/",
        json={
            "id": "Q99004",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Undeleted"}},
        },
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 410

    logger.info("✓ Hard delete prevents undelete")
