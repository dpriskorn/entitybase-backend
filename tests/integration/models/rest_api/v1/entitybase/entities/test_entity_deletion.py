import logging

import pytest
import requests


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
    api_client.post(f"{base_url}/entity", json=entity_data, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})

    # Hard delete
    delete_response = api_client.delete(
        f"{base_url}/entity/Q99002",
        json={"delete_type": "hard"},
        headers={"X-Edit-Summary": "delete entity", "X-User-ID": "0"},
    )
    assert delete_response.status_code == 200

    result = delete_response.json()
    assert result["id"] == "Q99002"
    assert result["is_deleted"] is True
    assert result["deletion_type"] == "hard"

    # Verify entity no longer accessible (hard delete hides)
    get_response = api_client.get(f"{base_url}/entity/Q99002")
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
    api_client.post(f"{base_url}/entity", json=entity_data, headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"})

    # Hard delete
    api_client.delete(
        f"{base_url}/entity/Q99004",
        json={"delete_type": "hard"},
        headers={"X-Edit-Summary": "delete entity", "X-User-ID": "0"},
    )

    # Try to undelete (should fail with 410)
    response = api_client.post(
        f"{base_url}/entity",
        json={
            "id": "Q99004",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Undeleted"}},
        },
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )
    assert response.status_code == 410

    logger.info("✓ Hard delete prevents undelete")
