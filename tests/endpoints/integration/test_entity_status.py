import json
import logging
from typing import Any, Dict, cast

import pytest
import requests

from rapidhash import rapidhash


def test_status_flags_stored_in_s3(api_client: requests.Session, base_url: str) -> None:
    """All status flags should be stored in S3"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q90004",
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
            "is_dangling": True,
            "is_mass_edit_protected": False,
        },
    )

    raw = api_client.get(f"{base_url}/raw/Q90004/1").json()
    assert raw["is_semi_protected"]
    assert not raw["is_locked"]
    assert not raw["is_archived"]
    assert raw["is_dangling"]
    assert not raw["is_mass_edit_protected"]

    logger.info("✓ Status flags stored in S3")


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


def test_dangling_flag_set_by_frontend(
    api_client: requests.Session, base_url: str
) -> None:
    """is_dangling should be set by frontend, not computed by backend"""
    logger = logging.getLogger(__name__)

    # Entity without P6104 (frontend sets is_dangling=True)
    entity_no_wp = {"id": "Q90006", "type": "item", "claims": {}}
    api_client.post(f"{base_url}/entity", json={**entity_no_wp, "is_dangling": True})
    raw = api_client.get(f"{base_url}/raw/Q90006/1").json()
    assert raw["is_dangling"]

    # Entity with P6104 (frontend sets is_dangling=False)
    entity_with_wp = {"id": "Q90007", "type": "item", "claims": {"P6104": []}}
    api_client.post(f"{base_url}/entity", json={**entity_with_wp, "is_dangling": False})
    raw = api_client.get(f"{base_url}/raw/Q90007/1").json()
    assert not raw["is_dangling"]

    logger.info("✓ is_dangling flag set by frontend")