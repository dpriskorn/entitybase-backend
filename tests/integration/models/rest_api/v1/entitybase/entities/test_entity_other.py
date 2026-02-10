import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_lexeme(api_prefix: str) -> None:
    """Test updating a lexeme entity"""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    # Create lexeme
    lexeme_data = {
        "type": "lexeme",
        "lemmas": {"en": {"language": "en", "value": "test"}},
        "lexicalCategory": "Q1084",  # noun
        "language": "Q1860",  # English
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            f"{api_prefix}/entities/lexemes", json=lexeme_data, headers={"X-Edit-Summary": "create lexeme", "X-User-ID": "0"}
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

        response = await client.put(
            f"{api_prefix}/entities/lexemes/{lexeme_id}", json=updated_lexeme_data, headers={"X-Edit-Summary": "update lexeme", "X-User-ID": "0"}
        )
        assert response.status_code == 200

        result = response.json()
        assert result["id"] == lexeme_id
        assert result["revision_id"] == 2
        assert result["data"]["lemmas"]["en"]["value"] == "updated test"

        logger.info("✓ Lexeme update works correctly")
