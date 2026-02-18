"""Contract tests for entity status endpoints.

These tests verify the entity status endpoints conform to their API contract.
"""

import sys

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_lock_response_schema(api_prefix: str) -> None:
    """Contract test: Lock response contains required fields."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test Entity"}},
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        lock_resp = await client.post(
            f"{api_prefix}/entities/{entity_id}/lock",
            headers={"X-Edit-Summary": "lock", "X-User-ID": "0"},
        )
        assert lock_resp.status_code == 200
        data = lock_resp.json()

        assert "id" in data
        assert "rev_id" in data
        assert "status" in data
        assert "idempotent" in data
        assert data["status"] == "locked"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_unlock_response_schema(api_prefix: str) -> None:
    """Contract test: Unlock response contains required fields."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test Entity"}},
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        await client.post(
            f"{api_prefix}/entities/{entity_id}/lock",
            headers={"X-Edit-Summary": "lock", "X-User-ID": "0"},
        )

        unlock_resp = await client.delete(
            f"{api_prefix}/entities/{entity_id}/lock",
            headers={"X-Edit-Summary": "unlock", "X-User-ID": "0"},
        )
        assert unlock_resp.status_code == 200
        data = unlock_resp.json()

        assert "id" in data
        assert "rev_id" in data
        assert "status" in data
        assert "idempotent" in data
        assert data["status"] == "unlocked"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_archive_response_schema(api_prefix: str) -> None:
    """Contract test: Archive response contains required fields."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test Entity"}},
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        archive_resp = await client.post(
            f"{api_prefix}/entities/{entity_id}/archive",
            headers={"X-Edit-Summary": "archive", "X-User-ID": "0"},
        )
        assert archive_resp.status_code == 200
        data = archive_resp.json()

        assert "id" in data
        assert "rev_id" in data
        assert "status" in data
        assert "idempotent" in data
        assert data["status"] == "archived"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_unarchive_response_schema(api_prefix: str) -> None:
    """Contract test: Unarchive response contains required fields."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test Entity"}},
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        await client.post(
            f"{api_prefix}/entities/{entity_id}/archive",
            headers={"X-Edit-Summary": "archive", "X-User-ID": "0"},
        )

        unarchive_resp = await client.delete(
            f"{api_prefix}/entities/{entity_id}/archive",
            headers={"X-Edit-Summary": "unarchive", "X-User-ID": "0"},
        )
        assert unarchive_resp.status_code == 200
        data = unarchive_resp.json()

        assert "id" in data
        assert "rev_id" in data
        assert "status" in data
        assert "idempotent" in data
        assert data["status"] == "unarchived"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_semi_protect_response_schema(api_prefix: str) -> None:
    """Contract test: Semi-protect response contains required fields."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test Entity"}},
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        protect_resp = await client.post(
            f"{api_prefix}/entities/{entity_id}/semi-protect",
            headers={"X-Edit-Summary": "semi-protect", "X-User-ID": "0"},
        )
        assert protect_resp.status_code == 200
        data = protect_resp.json()

        assert "id" in data
        assert "rev_id" in data
        assert "status" in data
        assert "idempotent" in data
        assert data["status"] == "semi_protected"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_mass_edit_protect_response_schema(api_prefix: str) -> None:
    """Contract test: Mass-edit-protect response contains required fields."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test Entity"}},
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        protect_resp = await client.post(
            f"{api_prefix}/entities/{entity_id}/mass-edit-protect",
            headers={"X-Edit-Summary": "mass-edit-protect", "X-User-ID": "0"},
        )
        assert protect_resp.status_code == 200
        data = protect_resp.json()

        assert "id" in data
        assert "rev_id" in data
        assert "status" in data
        assert "idempotent" in data
        assert data["status"] == "mass_edit_protected"


@pytest.mark.contract
@pytest.mark.asyncio
@pytest.mark.xfail(reason="Contract test mock doesn't persist entity state between revisions")
async def test_status_idempotent_flag(api_prefix: str) -> None:
    """Contract test: Idempotent flag is true when entity is already in target state."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            f"{api_prefix}/entities/items",
            json={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test Entity Idempotent"}},
            },
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_resp.status_code == 200
        entity_id = create_resp.json()["id"]

        first_lock_resp = await client.post(
            f"{api_prefix}/entities/{entity_id}/lock",
            headers={"X-Edit-Summary": "lock", "X-User-ID": "0"},
        )
        assert first_lock_resp.status_code == 200

        lock_again_resp = await client.post(
            f"{api_prefix}/entities/{entity_id}/lock",
            headers={"X-Edit-Summary": "lock again", "X-User-ID": "0"},
        )
        assert lock_again_resp.status_code == 200
        data = lock_again_resp.json()

        assert data["idempotent"] is True
