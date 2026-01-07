import logging

import pytest

import requests


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_entities_endpoint_requires_filter(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that /entities endpoint requires either status or edit_type filter"""
    logger = logging.getLogger(__name__)

    response = api_client.get(f"{base_url}/entities")
    assert response.status_code == 400
    assert "filter" in response.json()["detail"].lower()

    logger.info("✓ /entities requires filter parameter")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_entities_invalid_status(api_client: requests.Session, base_url: str) -> None:
    """Test that /entities returns 400 for invalid status value"""
    logger = logging.getLogger(__name__)

    response = api_client.get(f"{base_url}/entities?status=invalid")
    assert response.status_code == 400

    logger.info("✓ /entities validates status parameter")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_locked_entities(api_client: requests.Session, base_url: str) -> None:
    """Test that /entities?status=locked returns locked items"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90010",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Locked"}},
    }
    api_client.post(f"{base_url}/entity", json={**entity_data, "is_locked": True})

    response = api_client.get(f"{base_url}/entities?status=locked")
    assert response.status_code == 200
    result = response.json()
    assert "entities" in result
    assert "count" in result
    assert isinstance(result["entities"], list)
    assert isinstance(result["count"], int)
    assert any(e["entity_id"] == "Q90010" for e in result["entities"])

    for entity in result["entities"]:
        assert "entity_id" in entity
        assert "head_revision_id" in entity

    logger.info("✓ List locked entities works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_semi_protected_entities(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that /entities?status=semi_protected returns semi-protected items"""
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
    result = response.json()
    assert "entities" in result
    assert "count" in result
    assert any(e["entity_id"] == "Q90011" for e in result["entities"])

    logger.info("✓ List semi-protected entities works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_archived_entities(api_client: requests.Session, base_url: str) -> None:
    """Test that /entities?status=archived returns archived items"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90012",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Archived"}},
    }
    api_client.post(f"{base_url}/entity", json={**entity_data, "is_archived": True})

    response = api_client.get(f"{base_url}/entities?status=archived")
    assert response.status_code == 200
    result = response.json()
    assert "entities" in result
    assert "count" in result
    assert any(e["entity_id"] == "Q90012" for e in result["entities"])

    logger.info("✓ List archived entities works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_dangling_entities(api_client: requests.Session, base_url: str) -> None:
    """Test that /entities?status=dangling returns dangling items"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90013",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Dangling"}},
    }
    api_client.post(f"{base_url}/entity", json={**entity_data, "is_dangling": True})

    response = api_client.get(f"{base_url}/entities?status=dangling")
    assert response.status_code == 200
    result = response.json()
    assert "entities" in result
    assert "count" in result
    assert any(e["entity_id"] == "Q90013" for e in result["entities"])

    logger.info("✓ List dangling entities works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_by_edit_type_lock_added(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that /entities?edit_type=lock-added returns entities with lock-added edit type"""
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
    result = response.json()
    assert "entities" in result
    assert "count" in result
    assert any(e["entity_id"] == "Q90014" for e in result["entities"])

    for entity in result["entities"]:
        assert "entity_id" in entity
        assert "edit_type" in entity
        assert "revision_id" in entity

    logger.info("✓ List by edit_type lock-added works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_by_edit_type_lock_removed(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that /entities?edit_type=lock-removed returns entities with lock-removed edit type"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90015",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    api_client.post(
        f"{base_url}/entity",
        json={**entity_data, "is_locked": False, "edit_type": "lock-removed"},
    )

    response = api_client.get(f"{base_url}/entities?edit_type=lock-removed")
    assert response.status_code == 200
    result = response.json()
    assert any(e["entity_id"] == "Q90015" for e in result["entities"])

    logger.info("✓ List by edit_type lock-removed works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_by_edit_type_mass_protection_added(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that /entities?edit_type=mass-protection-added returns entities"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90016",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    api_client.post(
        f"{base_url}/entity",
        json={
            **entity_data,
            "is_mass_edit_protected": True,
            "edit_type": "mass-protection-added",
        },
    )

    response = api_client.get(f"{base_url}/entities?edit_type=mass-protection-added")
    assert response.status_code == 200
    result = response.json()
    assert any(e["entity_id"] == "Q90016" for e in result["entities"])

    logger.info("✓ List by edit_type mass-protection-added works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_by_edit_type_mass_protection_removed(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that /entities?edit_type=mass-protection-removed returns entities"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90017",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    api_client.post(
        f"{base_url}/entity",
        json={
            **entity_data,
            "is_mass_edit_protected": False,
            "edit_type": "mass-protection-removed",
        },
    )

    response = api_client.get(f"{base_url}/entities?edit_type=mass-protection-removed")
    assert response.status_code == 200
    result = response.json()
    assert any(e["entity_id"] == "Q90017" for e in result["entities"])

    logger.info("✓ List by edit_type mass-protection-removed works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_by_edit_type_soft_delete(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that /entities?edit_type=soft-delete returns entities"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90018",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "To Delete"}},
    }

    api_client.post(f"{base_url}/entity", json=entity_data)
    api_client.delete(f"{base_url}/entity/Q90018", json={"delete_type": "soft"})

    response = api_client.get(f"{base_url}/entities?edit_type=soft-delete")
    assert response.status_code == 200
    result = response.json()
    assert any(e["entity_id"] == "Q90018" for e in result["entities"])

    logger.info("✓ List by edit_type soft-delete works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_by_edit_type_redirect_create(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that /entities?edit_type=redirect-create returns entities"""
    logger = logging.getLogger(__name__)

    entity_from = {"id": "Q90019", "type": "item", "labels": {"en": {"value": "From"}}}
    entity_to = {"id": "Q90020", "type": "item", "labels": {"en": {"value": "To"}}}

    api_client.post(f"{base_url}/entity", json=entity_from)
    api_client.post(f"{base_url}/entity", json=entity_to)

    response = api_client.post(
        f"{base_url}/redirects",
        json={
            "redirect_from_id": "Q90019",
            "redirect_to_id": "Q90020",
            "created_by": "test-user",
        },
    )
    assert response.status_code == 200

    response = api_client.get(f"{base_url}/entities?edit_type=redirect-create")
    assert response.status_code == 200
    result = response.json()
    assert any(e["entity_id"] == "Q90019" for e in result["entities"])

    logger.info("✓ List by edit_type redirect-create works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_by_edit_type_redirect_revert(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that /entities?edit_type=redirect-revert returns entities"""
    logger = logging.getLogger(__name__)

    entity_from = {"id": "Q90021", "type": "item", "labels": {"en": {"value": "From"}}}
    entity_to = {"id": "Q90022", "type": "item", "labels": {"en": {"value": "To"}}}

    api_client.post(f"{base_url}/entity", json=entity_from)
    api_client.post(f"{base_url}/entity", json=entity_to)

    api_client.post(
        f"{base_url}/redirects",
        json={
            "redirect_from_id": "Q90021",
            "redirect_to_id": "Q90022",
            "created_by": "test-user",
        },
    )

    api_client.post(
        f"{base_url}/entities/Q90021/revert-redirect",
        json={
            "revert_to_revision_id": 1,
            "revert_reason": "test",
            "created_by": "test",
        },
    )

    response = api_client.get(f"{base_url}/entities?edit_type=redirect-revert")
    assert response.status_code == 200
    result = response.json()
    assert any(e["entity_id"] == "Q90021" for e in result["entities"])

    logger.info("✓ List by edit_type redirect-revert works")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_respects_limit(api_client: requests.Session, base_url: str) -> None:
    """Test that /entities respects the limit parameter"""
    logger = logging.getLogger(__name__)

    for i in range(10):
        entity_data = {
            "id": f"Q90{100 + i}",
            "type": "item",
            "labels": {"en": {"language": "en", "value": f"Test {i}"}},
        }
        api_client.post(f"{base_url}/entity", json={**entity_data, "is_locked": True})

    response = api_client.get(f"{base_url}/entities?status=locked&limit=5")
    assert response.status_code == 200
    result = response.json()
    assert result["count"] == 5
    assert len(result["entities"]) == 5

    logger.info("✓ List respects limit parameter")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_default_limit(api_client: requests.Session, base_url: str) -> None:
    """Test that /entities has a sensible default limit"""
    logger = logging.getLogger(__name__)

    response = api_client.get(f"{base_url}/entities?status=locked")
    assert response.status_code == 200
    result = response.json()
    assert "count" in result
    assert isinstance(result["count"], int)

    logger.info("✓ List uses default limit")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_empty_results(api_client: requests.Session, base_url: str) -> None:
    """Test that /entities returns empty array when no entities match filter"""
    logger = logging.getLogger(__name__)

    response = api_client.get(f"{base_url}/entities?status=locked")
    assert response.status_code == 200
    result = response.json()
    assert result["entities"] == []
    assert result["count"] == 0

    logger.info("✓ List returns empty results correctly")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_response_structure(api_client: requests.Session, base_url: str) -> None:
    """Test that /entities returns correct response structure"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90999",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }
    api_client.post(f"{base_url}/entity", json={**entity_data, "is_locked": True})

    response = api_client.get(f"{base_url}/entities?status=locked")
    assert response.status_code == 200
    result = response.json()

    assert "entities" in result
    assert "count" in result

    for entity in result["entities"]:
        assert "entity_id" in entity
        assert isinstance(entity["entity_id"], str)
        assert "head_revision_id" in entity
        assert isinstance(entity["head_revision_id"], int)

    logger.info("✓ List returns correct response structure")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_edit_type_response_includes_edit_type(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that /entities with edit_type filter includes edit_type in results"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90998",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    api_client.post(
        f"{base_url}/entity",
        json={**entity_data, "edit_type": "custom-edit-type"},
    )

    response = api_client.get(f"{base_url}/entities?edit_type=custom-edit-type")
    assert response.status_code == 200
    result = response.json()

    for entity in result["entities"]:
        assert "entity_id" in entity
        assert "edit_type" in entity
        assert "revision_id" in entity

    logger.info("✓ List by edit_type includes edit_type field")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_multiple_filters_behavior(
    api_client: requests.Session, base_url: str
) -> None:
    """Test behavior when both status and edit_type are provided"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90997",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }
    api_client.post(f"{base_url}/entity", json=entity_data)

    response = api_client.get(f"{base_url}/entities?status=locked&edit_type=lock-added")
    assert response.status_code == 200

    result = response.json()
    assert "entities" in result
    assert "count" in result

    logger.info("✓ List handles multiple filters")


@pytest.mark.skip(
    reason="Endpoint not implemented yet - /entities endpoint is disabled"
)
def test_list_large_limit(api_client: requests.Session, base_url: str) -> None:
    """Test that /entities handles large limit values"""
    logger = logging.getLogger(__name__)

    response = api_client.get(f"{base_url}/entities?status=locked&limit=1000")
    assert response.status_code == 200
    result = response.json()
    assert "entities" in result
    assert "count" in result

    logger.info("✓ List handles large limit values")
