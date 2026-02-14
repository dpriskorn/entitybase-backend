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
        "lexical_category": "Q1084",
        "language": "Q1860",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "create lexeme", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        lexeme_id = create_response.json()["id"]

        # Update lexeme
        updated_lexeme_data = {
            "data": {
                "type": "lexeme",
                "lemmas": {"en": {"language": "en", "value": "updated test"}},
                "lexical_category": "Q1084",
                "language": "Q1860",
            }
        }

        response = await client.put(
            f"{api_prefix}/entities/lexemes/{lexeme_id}",
            json=updated_lexeme_data,
            headers={"X-Edit-Summary": "update lexeme", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        result = response.json()
        assert result["id"] == lexeme_id
        assert result["revision_id"] == 2
        assert result["data"]["lemmas"]["en"]["value"] == "updated test"

        logger.info("✓ Lexeme update works correctly")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_lexeme_lemmas_endpoints(api_prefix: str) -> None:
    """Test lexeme lemma endpoints."""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    # Create lexeme with lemmas
    lexeme_data = {
        "type": "lexeme",
        "lemmas": {
            "en": {"language": "en", "value": "answer"},
            "de": {"language": "de", "value": "Antwort"},
        },
        "lexical_category": "Q1084",
        "language": "Q1860",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "create lexeme", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        lexeme_id = create_response.json()["id"]

        # Get all lemmas
        get_lemmas_response = await client.get(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lemmas",
        )
        assert get_lemmas_response.status_code == 200
        lemmas = get_lemmas_response.json()["lemmas"]
        assert "en" in lemmas
        assert "de" in lemmas
        assert lemmas["en"]["value"] == "answer"
        logger.info("✓ Get all lemmas works correctly")

        # Get single lemma
        get_lemma_response = await client.get(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lemmas/en",
        )
        assert get_lemma_response.status_code == 200
        assert get_lemma_response.json()["value"] == "answer"
        logger.info("✓ Get single lemma works correctly")

        # Update lemma
        update_lemma_response = await client.put(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lemmas/en",
            json={"language": "en", "value": "reply"},
            headers={"X-Edit-Summary": "update lemma", "X-User-ID": "0"},
        )
        assert update_lemma_response.status_code == 200
        assert update_lemma_response.json()["data"]["lemmas"]["en"]["value"] == "reply"
        logger.info("✓ Update lemma works correctly")

        delete_last_lemma_response = await client.delete(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lemmas/en",
            headers={"X-Edit-Summary": "delete lemma", "X-User-ID": "0"},
        )
        assert delete_last_lemma_response.status_code == 400
        assert (
            "at least one lemma" in delete_last_lemma_response.json()["detail"].lower()
        )
        logger.info("✓ Delete last lemma correctly fails")

        # Delete one lemma (there are still 2, so should succeed)
        delete_lemma_response = await client.delete(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lemmas/de",
            headers={"X-Edit-Summary": "delete lemma", "X-User-ID": "0"},
        )
        assert delete_lemma_response.status_code == 200

        # Verify only en lemma remains
        verify_response = await client.get(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lemmas",
        )
        lemmas_after = verify_response.json()["lemmas"]
        assert "en" in lemmas_after
        assert "de" not in lemmas_after
        logger.info("✓ Delete lemma works correctly")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_lexeme_without_lemmas_fails(api_prefix: str) -> None:
    """Test that creating a lexeme without lemmas fails."""
    from models.rest_api.main import app

    logger = logging.getLogger(__name__)

    # Try to create lexeme without lemmas
    lexeme_data = {
        "type": "lexeme",
        "lemmas": {},
        "lexical_category": "Q1084",
        "language": "Q1860",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "create lexeme", "X-User-ID": "0"},
        )
        assert response.status_code == 400
        assert "at least one lemma" in str(response.json()["message"]).lower()
        logger.info("✓ Create lexeme without lemmas correctly fails")
