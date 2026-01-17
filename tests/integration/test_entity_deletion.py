import json
import logging
from typing import Any, Dict, cast

import pytest
import requests

from rapidhash import rapidhash


def test_soft_delete_entity(api_client: requests.Session, base_url: str) -> None:
    """Test soft deleting an entity"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q99001",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "To Delete"}},
    }

    # Create entity
    api_client.post(f"{base_url}/entity", json=entity_data)

    # Soft delete
    delete_response = api_client.delete(
        f"{base_url}/entity/Q99001",
        json={"delete_type": "soft"},
    )
    assert delete_response.status_code == 200

    result = delete_response.json()
    assert result["id"] == "Q99001"
    assert result["is_deleted"] is True
    assert result["deletion_type"] == "soft"
    assert "revision_id" in result

    # Verify entity still accessible (soft delete doesn't hide)
    get_response = api_client.get(f"{base_url}/entity/Q99001")
    assert get_response.status_code == 200

    # Verify deletion revision in S3
    revision_response = api_client.get(f"{base_url}/raw/Q99001/2")
    raw_data = revision_response.json()
    assert raw_data["is_deleted"] is True
    assert raw_data["edit_type"] == "soft-delete"
    assert "entity" in raw_data  # Entity data preserved

    logger.info("✓ Soft delete works correctly")


def test_hard_delete_entity(api_client: requests.Session, base_url: str) -> None:
    """Test hard deleting an entity"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q99002",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "To Hard Delete"}},
    }

    # Create entity
    api_client.post(f"{base_url}/entity", json=entity_data)

    # Hard delete
    delete_response = api_client.delete(
        f"{base_url}/entity/Q99002",
        json={"delete_type": "hard"},
    )
    assert delete_response.status_code == 200

    result = delete_response.json()
    assert result["id"] == "Q99002"
    assert result["is_deleted"] is True
    assert result["deletion_type"] == "hard"

    # Verify entity no longer accessible (hard delete hides)
    get_response = api_client.get(f"{base_url}/entity/Q99002")
    assert get_response.status_code == 410  # Gone
    assert "deleted" in get_response.json()["detail"].lower()

    logger.info("✓ Hard delete hides entity correctly")


def test_undelete_entity(api_client: requests.Session, base_url: str) -> None:
    """Test undeleting an entity by creating new revision"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q99003",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Original"}},
    }

    # Create entity
    api_client.post(f"{base_url}/entity", json=entity_data)

    # Soft delete
    api_client.delete(
        f"{base_url}/entity/Q99003",
        json={
            "delete_type": "soft",
        },
    )

    # Undelete by creating new revision
    undelete_response = api_client.post(
        f"{base_url}/entity",
        json={
            "id": "Q99003",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Undeleted"}},
        },
    )
    assert undelete_response.status_code == 200

    result = undelete_response.json()
    assert result["revision_id"] == 3  # Original (1) + Delete (2) + Undelete (3)

    # Verify entity accessible again
    get_response = api_client.get(f"{base_url}/entity/Q99003")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["labels"]["en"]["value"] == "Undeleted"

    # Verify latest revision not deleted
    raw_response = api_client.get(f"{base_url}/raw/Q99003/3")
    assert raw_response.json()["is_deleted"] is False

    logger.info("✓ Undelete via new revision works")


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
    api_client.post(f"{base_url}/entity", json=entity_data)

    # Hard delete
    api_client.delete(
        f"{base_url}/entity/Q99004",
        json={"delete_type": "hard"},
    )

    # Try to undelete (should fail with 410)
    response = api_client.post(
        f"{base_url}/entity",
        json={
            "id": "Q99004",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Undeleted"}},
        },
    )
    assert response.status_code == 410

    logger.info("✓ Hard delete prevents undelete")