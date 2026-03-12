import logging
import sys

sys.path.insert(0, "src")

import pytest
from httpx import ASGITransport, AsyncClient


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
        result = update_lemma_response.json()
        assert "hash" in result
        assert isinstance(result["hash"], int)
        logger.info("✓ Update lemma works correctly")

        delete_lemma_response = await client.delete(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lemmas/de",
            headers={"X-Edit-Summary": "delete lemma", "X-User-ID": "0"},
        )
        assert delete_lemma_response.status_code == 200
        assert delete_lemma_response.json()["success"] is True

        delete_last_lemma_response = await client.delete(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lemmas/en",
            headers={"X-Edit-Summary": "delete lemma", "X-User-ID": "0"},
        )
        assert delete_last_lemma_response.status_code == 400
        assert (
            "at least one lemma" in delete_last_lemma_response.json()["message"].lower()
        )
        logger.info("✓ Delete last lemma correctly fails")

        # Verify: de was deleted in step 1, en still exists (step 2 failed)
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


@pytest.mark.asyncio
@pytest.mark.integration
async def test_export_entity_to_turtle(api_prefix: str) -> None:
    """Test exporting entity to Turtle format."""
    from models.rest_api.main import app

    entity_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Turtle Export Test"}},
        "descriptions": {
            "en": {"language": "en", "value": "A test entity for turtle export"}
        },
        "aliases": {"en": [{"language": "en", "value": "Test Entity"}]},
        "claims": {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datatype": "wikibase-item",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q5"},
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                }
            ]
        },
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity first
        create_response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "create test entity", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        entity_id = create_response.json()["data"]["entity_id"]

        # Export to turtle
        response = await client.get(f"{api_prefix}/entities/{entity_id}.ttl")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/turtle; charset=utf-8"
        turtle_content = response.text
        assert len(turtle_content) > 0
        # Turtle format should contain prefixes
        assert "@prefix" in turtle_content or "http://" in turtle_content


@pytest.mark.asyncio
@pytest.mark.integration
async def test_export_nonexistent_entity_returns_404(api_prefix: str) -> None:
    """Test exporting nonexistent entity returns 404."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/entities/Q99999.ttl")
        assert response.status_code == 404
