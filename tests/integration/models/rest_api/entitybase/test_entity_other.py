import logging

import pytest
import requests


@pytest.mark.integration
def test_update_lexeme(api_client: requests.Session, base_url: str) -> None:
    """Test updating a lexeme entity"""
    logger = logging.getLogger(__name__)

    # Create lexeme
    lexeme_data = {
        "type": "lexeme",
        "lemmas": {"en": {"language": "en", "value": "test"}},
        "lexicalCategory": "Q1084",  # noun
        "language": "Q1860",  # English
    }

    create_response = api_client.post(
        f"{base_url}/entitybase/v1/entities/lexemes", json=lexeme_data
    )
    assert create_response.status_code == 200
    lexeme_id = create_response.json()["id"]

    # Update lexeme
    updated_lexeme_data = {
        "data": {
            "type": "lexeme",
            "lemmas": {"en": {"language": "en", "value": "updated test"}},
            "lexicalCategory": "Q1084",
            "language": "Q1860",
        }
    }

    response = api_client.put(
        f"{base_url}/entitybase/v1/lexeme/{lexeme_id}", json=updated_lexeme_data
    )
    assert response.status_code == 200

    result = response.json()
    assert result["id"] == lexeme_id
    assert result["revision_id"] == 2
    assert result["data"]["lemmas"]["en"]["value"] == "updated test"

    logger.info("✓ Lexeme update works correctly")
