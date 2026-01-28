import logging

import pytest
import requests


@pytest.mark.integration
def test_semi_protection_blocks_not_autoconfirmed_users(
    api_client: requests.Session, base_url: str
) -> None:
    """Semi-protected items should block not-autoconfirmed users"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90001",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    # Create semi-protected item
    api_client.post(
        f"{base_url}/entity", json={**entity_data, "is_semi_protected": True}
    )

    # Attempt edit by not-autoconfirmed user (should fail)
    response = api_client.post(
        f"{base_url}/entity",
        json={
            **entity_data,
            "labels": {"en": {"language": "en", "value": "Updated"}},
            "is_not_autoconfirmed_user": True,
        },
    )
    assert response.status_code == 403
    assert "unconfirmed" in response.json()["message"].lower()

    # Autoconfirmed user should be able to edit
    response = api_client.post(
        f"{base_url}/entity",
        json={
            **entity_data,
            "labels": {"en": {"language": "en", "value": "Updated"}},
            "is_not_autoconfirmed_user": False,
        },
    )
    assert response.status_code == 200

    logger.info("✓ Semi-protection blocks not-autoconfirmed users")


@pytest.mark.integration
def test_semi_protection_allows_autoconfirmed_users(
    api_client: requests.Session, base_url: str
) -> None:
    """Semi-protected items should allow autoconfirmed users to edit"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90001b",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    # Create semi-protected item
    api_client.post(
        f"{base_url}/entity", json={**entity_data, "is_semi_protected": True}
    )

    # Autoconfirmed user edit should succeed
    response = api_client.post(
        f"{base_url}/entity",
        json={
            **entity_data,
            "labels": {"en": {"language": "en", "value": "Updated"}},
            "is_not_autoconfirmed_user": False,
        },
    )
    assert response.status_code == 200

    logger.info("✓ Semi-protection allows autoconfirmed users")


@pytest.mark.integration
def test_locked_items_block_all_edits(
    api_client: requests.Session, base_url: str
) -> None:
    """Locked items should reject all edits"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90002",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    # Create locked item
    api_client.post(f"{base_url}/entity", json={**entity_data, "is_locked": True})

    # Attempt manual edit (should fail)
    response = api_client.post(
        f"{base_url}/entity",
        json={**entity_data, "labels": {"en": {"language": "en", "value": "Updated"}}},
    )
    assert response.status_code == 403
    assert "locked" in response.json()["message"].lower()

    logger.info("✓ Locked items block all edits")


@pytest.mark.integration
def test_archived_items_block_all_edits(
    api_client: requests.Session, base_url: str
) -> None:
    """Archived items should reject all edits with distinct error"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90003",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    # Create archived item
    api_client.post(f"{base_url}/entity", json={**entity_data, "is_archived": True})

    # Attempt edit (should fail)
    response = api_client.post(
        f"{base_url}/entity",
        json={**entity_data, "labels": {"en": {"language": "en", "value": "Updated"}}},
    )
    assert response.status_code == 403
    assert "archived" in response.json()["message"].lower()

    logger.info("✓ Archived items block all edits")


@pytest.mark.integration
def test_mass_edit_protection_blocks_mass_edits(
    api_client: requests.Session, base_url: str
) -> None:
    """Mass-edit protected items should block mass edits"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90015",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    # Create mass-edit protected item
    api_client.post(
        f"{base_url}/entity", json={**entity_data, "is_mass_edit_protected": True}
    )

    # Attempt mass edit (should fail)
    response = api_client.post(
        f"{base_url}/entity",
        json={
            **entity_data,
            "is_mass_edit": True,
            "labels": {"en": {"language": "en", "value": "Updated"}},
        },
    )
    assert response.status_code == 403
    assert "mass edits blocked" in response.json()["message"].lower()

    # Manual edit should work
    response = api_client.post(
        f"{base_url}/entity",
        json={
            **entity_data,
            "is_mass_edit": False,
            "labels": {"en": {"language": "en", "value": "Updated manually"}},
        },
    )
    assert response.status_code == 200

    logger.info("✓ Mass-edit protection works correctly")



