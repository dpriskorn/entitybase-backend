import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skip(
    reason="Semi-protection for regular edits not implemented, only mass edits"
)
async def test_semi_protection_blocks_not_autoconfirmed_users(api_prefix: str) -> None:
    """Semi-protected items should block not-autoconfirmed users for mass edits"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90001",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json={**entity_data, "is_semi_protected": True},
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.post(
            f"{api_prefix}/entities/items",
            json={
                **entity_data,
                "labels": {"en": {"language": "en", "value": "Updated"}},
                "is_mass_edit": True,
                "is_autoconfirmed_user": False,
            },
            headers={"X-Edit-Summary": "mass update entity", "X-User-ID": "0"},
        )
        assert response.status_code == 403
        assert "semi-protected" in response.json()["message"].lower()

        logger.info("✓ Semi-protection blocks mass edits by not-autoconfirmed users")


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skip(reason="Protection for regular edits not implemented")
async def test_semi_protection_allows_autoconfirmed_users(api_prefix: str) -> None:
    """Semi-protected items should allow autoconfirmed users to edit"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90001b",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json={**entity_data, "is_semi_protected": True},
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        response = await client.post(
            f"{api_prefix}/entities/items",
            json={
                **entity_data,
                "labels": {"en": {"language": "en", "value": "Updated"}},
                "is_autoconfirmed_user": True,
            },
            headers={"X-Edit-Summary": "update entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        logger.info("✓ Semi-protection allows autoconfirmed users")


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skip(reason="Lock protection for edits not implemented")
async def test_locked_items_block_all_edits(api_prefix: str) -> None:
    """Locked items should reject all edits"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90002",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create locked item
        await client.post(
            f"{api_prefix}/entities/items",
            json={**entity_data, "is_locked": True},
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        # Attempt manual edit (should fail)
        response = await client.post(
            f"{api_prefix}/entities/items",
            json={
                **entity_data,
                "labels": {"en": {"language": "en", "value": "Updated"}},
            },
            headers={"X-Edit-Summary": "update entity", "X-User-ID": "0"},
        )
        assert response.status_code == 403
        assert "locked" in response.json()["message"].lower()

        logger.info("✓ Locked items block all edits")


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skip(reason="Archive protection for edits not implemented")
async def test_archived_items_block_all_edits(api_prefix: str) -> None:
    """Archived items should reject all edits with distinct error"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90003",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create archived item
        await client.post(
            f"{api_prefix}/entities/items",
            json={**entity_data, "is_archived": True},
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        # Attempt edit (should fail)
        response = await client.post(
            f"{api_prefix}/entities/items",
            json={
                **entity_data,
                "labels": {"en": {"language": "en", "value": "Updated"}},
            },
            headers={"X-Edit-Summary": "update entity", "X-User-ID": "0"},
        )
        assert response.status_code == 403
        assert "archived" in response.json()["message"].lower()

        logger.info("✓ Archived items block all edits")


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skip(reason="Mass-edit protection validation not implemented")
async def test_mass_edit_protection_blocks_mass_edits(api_prefix: str) -> None:
    """Mass-edit protected items should block mass edits"""
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
        # Create mass-edit protected item
        await client.post(
            f"{api_prefix}/entities/items",
            json={**entity_data, "is_mass_edit_protected": True},
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )

        # Attempt mass edit (should fail)
        response = await client.post(
            f"{api_prefix}/entities/items",
            json={
                **entity_data,
                "is_mass_edit": True,
                "labels": {"en": {"language": "en", "value": "Updated"}},
            },
            headers={"X-Edit-Summary": "mass update entity", "X-User-ID": "0"},
        )
        assert response.status_code == 403
        assert "mass edits blocked" in response.json()["message"].lower()

        # Manual edit should work
        response = await client.post(
            f"{api_prefix}/entities/items",
            json={
                **entity_data,
                "is_mass_edit": False,
                "labels": {"en": {"language": "en", "value": "Updated manually"}},
            },
            headers={"X-Edit-Summary": "update entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        logger.info("✓ Mass-edit protection works correctly")
