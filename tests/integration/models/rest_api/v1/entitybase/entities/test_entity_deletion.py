import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hard_delete_entity(api_prefix: str) -> None:
    """Test hard deleting an entity"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]

        delete_response = await client.request(
            "DELETE",
            f"{api_prefix}/entities/{entity_id}",
            json={"delete_type": "hard"},
            headers={
                "X-Edit-Summary": "delete entity",
                "X-User-ID": "0",
                "Content-Type": "application/json",
            },
        )
        assert delete_response.status_code == 200

        result = delete_response.json()
        assert result["id"] == entity_id
        assert result["is_deleted"] is True
        assert result["del_type"] == "hard"

        get_response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert get_response.status_code == 404
        assert "deleted" in get_response.json()["message"].lower()

        logger.info("✓ Hard delete hides entity correctly")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hard_delete_prevents_undelete(api_prefix: str) -> None:
    """Test that hard deleted entities cannot be undeleted"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]

        await client.request(
            "DELETE",
            f"{api_prefix}/entities/{entity_id}",
            json={"delete_type": "hard"},
            headers={
                "X-Edit-Summary": "delete entity",
                "X-User-ID": "0",
                "Content-Type": "application/json",
            },
        )

        response = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "id": entity_id,
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Undeleted"}},
            },
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 409

        logger.info("✓ Hard delete prevents undelete")
