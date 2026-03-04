import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_status_flags_returned_in_response(api_prefix: str) -> None:
    """Status flags should be returned in API response"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        data = response.json()
        assert "state" in data
        state = data["state"]
        assert "sp" in state
        assert "locked" in state
        assert "archived" in state
        assert "dangling" in state
        assert "mep" in state

        logger.info("✓ Status flags returned in API response")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_lock_entity(api_prefix: str) -> None:
    """Test locking an entity"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        response = await client.post(
            f"{api_prefix}/entities/{entity_id}/lock",
            headers={"X-Edit-Summary": "lock entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entity_id
        assert data["status"] == "locked"
        assert data["idempotent"] is False
        assert data["rev_id"] == 2

        logger.info("✓ Entity locked successfully")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_unlock_entity(api_prefix: str) -> None:
    """Test unlocking an entity"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        await client.post(
            f"{api_prefix}/entities/{entity_id}/lock",
            headers={"X-Edit-Summary": "lock entity", "X-User-ID": "0"},
        )

        response = await client.delete(
            f"{api_prefix}/entities/{entity_id}/lock",
            headers={"X-Edit-Summary": "unlock entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entity_id
        assert data["status"] == "unlocked"
        assert data["idempotent"] is False
        assert data["rev_id"] == 3

        logger.info("✓ Entity unlocked successfully")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_lock_idempotent(api_prefix: str) -> None:
    """Test locking an already locked entity returns idempotent response"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        await client.post(
            f"{api_prefix}/entities/{entity_id}/lock",
            headers={"X-Edit-Summary": "lock entity", "X-User-ID": "0"},
        )

        response = await client.post(
            f"{api_prefix}/entities/{entity_id}/lock",
            headers={"X-Edit-Summary": "lock again", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entity_id
        assert data["status"] == "locked"
        assert data["idempotent"] is True

        logger.info("✓ Idempotent lock works correctly")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_entity(api_prefix: str) -> None:
    """Test archiving an entity"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        response = await client.post(
            f"{api_prefix}/entities/{entity_id}/archive",
            headers={"X-Edit-Summary": "archive entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entity_id
        assert data["status"] == "archived"
        assert data["idempotent"] is False

        logger.info("✓ Entity archived successfully")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_unarchive_entity(api_prefix: str) -> None:
    """Test unarchiving an entity"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        await client.post(
            f"{api_prefix}/entities/{entity_id}/archive",
            headers={"X-Edit-Summary": "archive entity", "X-User-ID": "0"},
        )

        response = await client.delete(
            f"{api_prefix}/entities/{entity_id}/archive",
            headers={"X-Edit-Summary": "unarchive entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entity_id
        assert data["status"] == "unarchived"
        assert data["idempotent"] is False

        logger.info("✓ Entity unarchived successfully")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_semi_protect_entity(api_prefix: str) -> None:
    """Test semi-protecting an entity"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        response = await client.post(
            f"{api_prefix}/entities/{entity_id}/semi-protect",
            headers={"X-Edit-Summary": "semi-protect entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entity_id
        assert data["status"] == "semi_protected"
        assert data["idempotent"] is False

        logger.info("✓ Entity semi-protected successfully")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_mass_edit_protect_entity(api_prefix: str) -> None:
    """Test mass-edit protecting an entity"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        response = await client.post(
            f"{api_prefix}/entities/{entity_id}/mass-edit-protect",
            headers={"X-Edit-Summary": "mass-edit-protect entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entity_id
        assert data["status"] == "mass_edit_protected"
        assert data["idempotent"] is False

        logger.info("✓ Entity mass-edit protected successfully")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_mass_edit_unprotect_entity(api_prefix: str) -> None:
    """Test removing mass-edit protection from an entity"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        await client.post(
            f"{api_prefix}/entities/{entity_id}/mass-edit-protect",
            headers={"X-Edit-Summary": "mass-edit-protect entity", "X-User-ID": "0"},
        )

        response = await client.delete(
            f"{api_prefix}/entities/{entity_id}/mass-edit-protect",
            headers={"X-Edit-Summary": "mass-edit-unprotect entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entity_id
        assert data["status"] == "mass_edit_unprotected"
        assert data["idempotent"] is False

        logger.info("✓ Entity mass-edit unprotected successfully")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_status_not_found(api_prefix: str) -> None:
    """Test status endpoint returns 404 for non-existent entity"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/Q99999/lock",
            headers={"X-Edit-Summary": "lock entity", "X-User-ID": "0"},
        )
        assert response.status_code == 404

        logger.info("✓ 404 returned for non-existent entity")
