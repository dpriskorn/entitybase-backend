import logging

import pytest
import requests


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

    api_client.post(
        f"{base_url}/entity",
        json={
            **entity_data,
            "is_semi_protected": True,
            "is_locked": False,
            "is_archived": False,
            "is_dangling": False,
            "is_mass_edit_protected": True,
        },
    )

    response = api_client.get(f"{base_url}/entity/Q90005")
    data = response.json()
    assert data["is_semi_protected"]
    assert not data["is_locked"]
    assert not data["is_archived"]
    assert not data["is_dangling"]
    assert data["is_mass_edit_protected"]

    logger.info("✓ Status flags returned in API response")



