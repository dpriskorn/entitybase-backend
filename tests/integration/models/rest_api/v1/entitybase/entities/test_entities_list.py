import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_entities_endpoint_requires_filter(api_prefix: str) -> None:
    """Test that /entities endpoint requires either status or edit_type filter"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities")
        assert response.status_code == 400
        assert "filter" in response.json()["message"].lower()

        logger.info("✓ /entities requires filter parameter")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_entities_invalid_status(api_prefix: str) -> None:
    """Test that /entities returns 400 for invalid status value"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities?status=invalid")
        assert response.status_code == 400

        logger.info("✓ /entities validates status parameter")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_locked_entities(api_prefix: str) -> None:
    """Test that /entities?status=locked returns locked items"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90010",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Locked"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities",
            json={**entity_data, "is_locked": True},
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?status=locked")
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


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_semi_protected_entities(api_prefix: str) -> None:
    """Test that /entities?status=semi_protected returns semi-protected items"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90011",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Protected"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?status=semi_protected")
        assert response.status_code == 200
        result = response.json()
        assert "entities" in result
        assert "count" in result
        assert any(e["entity_id"] == "Q90011" for e in result["entities"])

        logger.info("✓ List semi-protected entities works")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_archived_entities(api_prefix: str) -> None:
    """Test that /entities?status=archived returns archived items"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90012",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Archived"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json={**entity_data, "is_archived": True},
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?status=archived")
        assert response.status_code == 200
        result = response.json()
        assert "entities" in result
        assert "count" in result
        assert any(e["entity_id"] == "Q90012" for e in result["entities"])

        logger.info("✓ List archived entities works")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_dangling_entities(api_prefix: str) -> None:
    """Test that /entities?status=dangling returns dangling items"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90013",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Dangling"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json={**entity_data, "is_dangling": True},
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?status=dangling")
        assert response.status_code == 200
        result = response.json()
        assert "entities" in result
        assert "count" in result
        assert any(e["entity_id"] == "Q90013" for e in result["entities"])

        logger.info("✓ List dangling entities works")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_by_edit_type_lock_added(api_prefix: str) -> None:
    """Test that /entities?edit_type=lock-added returns entities with lock-added edit type"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90014",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json={**entity_data, "is_locked": True, "edit_type": "lock-added"},
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?edit_type=lock-added")
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


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_by_edit_type_lock_removed(api_prefix: str) -> None:
    """Test that /entities?edit_type=lock-removed returns entities with lock-removed edit type"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90015",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json={**entity_data, "is_locked": False, "edit_type": "lock-removed"},
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?edit_type=lock-removed")
        assert response.status_code == 200
        result = response.json()
        assert any(e["entity_id"] == "Q90015" for e in result["entities"])

        logger.info("✓ List by edit_type lock-removed works")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_by_edit_type_mass_protection_added(api_prefix: str) -> None:
    """Test that /entities?edit_type=mass-protection-added returns entities"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90016",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json={
                **entity_data,
                "is_mass_edit_protected": True,
                "edit_type": "mass-protection-added",
            },
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.get(
            f"{api_prefix}/entities?edit_type=mass-protection-added"
        )
        assert response.status_code == 200
        result = response.json()
        assert any(e["entity_id"] == "Q90016" for e in result["entities"])

        logger.info("✓ List by edit_type mass-protection-added works")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_by_edit_type_mass_protection_removed(api_prefix: str) -> None:
    """Test that /entities?edit_type=mass-protection-removed returns entities"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90017",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json={
                **entity_data,
                "is_mass_edit_protected": False,
                "edit_type": "mass-protection-removed",
            },
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.get(
            f"{api_prefix}/entities?edit_type=mass-protection-removed"
        )
        assert response.status_code == 200
        result = response.json()
        assert any(e["entity_id"] == "Q90017" for e in result["entities"])

        logger.info("✓ List by edit_type mass-protection-removed works")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_by_edit_type_soft_delete(api_prefix: str) -> None:
    """Test that /entities?edit_type=soft-delete returns entities"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90018",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "To Delete"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities",
            json=entity_data,
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        await client.delete(
            f"{api_prefix}/entities/Q90018?delete_type=soft",
            headers={"X-Edit-Summary": "delete entity", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?edit_type=soft-delete")
        assert response.status_code == 200
        result = response.json()
        assert any(e["entity_id"] == "Q90018" for e in result["entities"])

        logger.info("✓ List by edit_type soft-delete works")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_by_edit_type_redirect_create(api_prefix: str) -> None:
    """Test that /entities?edit_type=redirect-create returns entities"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_from = {"id": "Q90019", "type": "item", "labels": {"en": {"value": "From"}}}
    entity_to = {"id": "Q90020", "type": "item", "labels": {"en": {"value": "To"}}}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities",
            json=entity_from,
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        await client.post(
            f"{api_prefix}/entities",
            json=entity_to,
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.post(
            f"{api_prefix}/redirects",
            json={
                "redirect_from_id": "Q90019",
                "redirect_to_id": "Q90020",
                "created_by": "test-user",
            },
            headers={"X-Edit-Summary": "create redirect", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities?edit_type=redirect-create")
        assert response.status_code == 200
        result = response.json()
        assert any(e["entity_id"] == "Q90019" for e in result["entities"])

        logger.info("✓ List by edit_type redirect-create works")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_by_edit_type_redirect_revert(api_prefix: str) -> None:
    """Test that /entities?edit_type=redirect-revert returns entities"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_from = {"id": "Q90021", "type": "item", "labels": {"en": {"value": "From"}}}
    entity_to = {"id": "Q90022", "type": "item", "labels": {"en": {"value": "To"}}}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities",
            json=entity_from,
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        await client.post(
            f"{api_prefix}/entities",
            json=entity_to,
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        await client.post(
            f"{api_prefix}/redirects",
            json={
                "redirect_from_id": "Q90021",
                "redirect_to_id": "Q90022",
                "created_by": "test-user",
            },
            headers={"X-Edit-Summary": "create redirect", "X-User-ID": "0"},
        )

        await client.post(
            f"{api_prefix}/entities/Q90021/revert-redirect",
            json={
                "revert_to_revision_id": 1,
                "revert_reason": "test",
                "created_by": "test",
            },
            headers={"X-Edit-Summary": "revert redirect", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?edit_type=redirect-revert")
        assert response.status_code == 200
        result = response.json()
        assert any(e["entity_id"] == "Q90021" for e in result["entities"])

        logger.info("✓ List by edit_type redirect-revert works")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_respects_limit(api_prefix: str) -> None:
    """Test that /entities respects the limit parameter"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        for i in range(10):
            entity_data = {
                "id": f"Q90{100 + i}",
                "type": "item",
                "labels": {"en": {"language": "en", "value": f"Test {i}"}},
            }
            await client.post(
                f"{api_prefix}/entities/items",
                json={**entity_data, "is_locked": True},
                headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
            )

        response = await client.get(f"{api_prefix}/entities?status=locked&limit=5")
        assert response.status_code == 200
        result = response.json()
        assert result["count"] == 5
        assert len(result["entities"]) == 5

        logger.info("✓ List respects limit parameter")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_default_limit(api_prefix: str) -> None:
    """Test that /entities has a sensible default limit"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities?status=locked")
        assert response.status_code == 200
        result = response.json()
        assert "count" in result
        assert isinstance(result["count"], int)

        logger.info("✓ List uses default limit")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_empty_results(api_prefix: str) -> None:
    """Test that /entities returns empty array when no entities match filter"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities?status=locked")
        assert response.status_code == 200
        result = response.json()
        assert result["entities"] == []
        assert result["count"] == 0

        logger.info("✓ List returns empty results correctly")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_response_structure(api_prefix: str) -> None:
    """Test that /entities returns correct response structure"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90999",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json={**entity_data, "is_locked": True},
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?status=locked")
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


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_edit_type_response_includes_edit_type(api_prefix: str) -> None:
    """Test that /entities with edit_type filter includes edit_type in results"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90998",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json={**entity_data, "edit_type": "custom-edit-type"},
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities?edit_type=custom-edit-type")
        assert response.status_code == 200
        result = response.json()

        for entity in result["entities"]:
            assert "entity_id" in entity
            assert "edit_type" in entity
            assert "revision_id" in entity

        logger.info("✓ List by edit_type includes edit_type field")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_multiple_filters_behavior(api_prefix: str) -> None:
    """Test behavior when both status and edit_type are provided"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90997",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.get(
            f"{api_prefix}/entities?status=locked&edit_type=lock-added"
        )
        assert response.status_code == 200

        result = response.json()
        assert "entities" in result
        assert "count" in result

        logger.info("✓ List handles multiple filters")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_large_limit(api_prefix: str) -> None:
    """Test that /entities handles large limit values"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities?status=locked&limit=1000")
        assert response.status_code == 200
        result = response.json()
        assert "entities" in result
        assert "count" in result

        logger.info("✓ List handles large limit values")
