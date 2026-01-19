import logging

import pytest
import requests


@pytest.mark.integration
def test_mass_edit_classification(api_client: requests.Session, base_url: str) -> None:
    """Test mass edit and edit_type classification"""
    logger = logging.getLogger(__name__)

    # Create mass edit with classification
    entity_data = {
        "id": "Q99994",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Mass Edit Test"}},
    }

    response = api_client.post(
        f"{base_url}/entity",
        json={
            "id": entity_data["id"],
            "type": entity_data["type"],
            "labels": entity_data["labels"],
            "is_mass_edit": True,
            "edit_type": "bot-import",
        },
    )
    assert response.status_code == 200

    result = response.json()
    assert result["id"] == "Q99994"
    assert result["revision_id"] == 1

    # Verify fields in S3
    raw_response = api_client.get(f"{base_url}/raw/Q99994/1")
    raw_data = raw_response.json()
    assert raw_data.get("is_mass_edit")
    assert raw_data.get("edit_type") == "bot-import"

    # Create manual edit (default behavior)
    manual_data = {
        "id": "Q99993",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Manual Test"}},
    }

    response2 = api_client.post(
        f"{base_url}/entity",
        json={
            "id": manual_data["id"],
            "type": manual_data["type"],
            "labels": manual_data["labels"],
        },
    )
    assert response2.status_code == 200

    # Verify defaults in S3
    raw_response2 = api_client.get(f"{base_url}/raw/Q99993/1")
    raw_data2 = raw_response2.json()
    assert not raw_data2.get("is_mass_edit")
    assert raw_data2.get("edit_type") == ""

    logger.info("✓ Mass edit classification works correctly")


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
    assert "unconfirmed" in response.json()["detail"].lower()

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
    assert "locked" in response.json()["detail"].lower()

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
    assert "archived" in response.json()["detail"].lower()

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
    assert "mass edits blocked" in response.json()["detail"].lower()

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


@pytest.mark.integration
def test_mass_protection_edit_types(
    api_client: requests.Session, base_url: str
) -> None:
    """Mass-protection edit types should work"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90016",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    # Add mass protection
    api_client.post(
        f"{base_url}/entity",
        json={
            **entity_data,
            "is_mass_edit_protected": True,
            "edit_type": "mass-protection-added",
        },
    )
    raw = api_client.get(f"{base_url}/raw/Q90016/1").json()
    assert raw["edit_type"] == "mass-protection-added"
    assert raw["is_mass_edit_protected"]

    # Remove mass protection
    api_client.post(
        f"{base_url}/entity",
        json={
            **entity_data,
            "is_mass_edit_protected": False,
            "edit_type": "mass-protection-removed",
        },
    )
    raw = api_client.get(f"{base_url}/raw/Q90016/2").json()
    assert raw["edit_type"] == "mass-protection-removed"
    assert not raw["is_mass_edit_protected"]

    logger.info("✓ Mass-protection edit types work")
