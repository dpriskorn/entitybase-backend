import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
def test_status_flags_returned_in_response(
    api_client: requests.Session, base_url: str
) -> None:
    """Status flags should be returned in API response"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90005",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test"}},
    }

    await client.post(
        "/v1/entitybase/entities/",
        json={
            **entity_data,
            "is_semi_protected": True,
            "is_locked": False,
            "is_archived": False,
            "is_dangling": False,
            "is_mass_edit_protected": True,
        },
        headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
    )

    response = await client.get("/v1/entitybase/entities//Q90005")
    data = response.json()
    assert data["is_semi_protected"]
    assert not data["is_locked"]
    assert not data["is_archived"]
    assert not data["is_dangling"]
    assert data["is_mass_edit_protected"]

    logger.info("✓ Status flags returned in API response")



