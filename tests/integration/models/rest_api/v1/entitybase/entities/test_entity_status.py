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

    entity_data = {
        "id": "Q90005",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(f"{api_prefix}/entities/Q90005")
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
