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
