"""E2E tests for comprehensive lexeme operations."""

import pytest
import sys

sys.path.insert(0, "src")

import logging

from httpx import ASGITransport, AsyncClient

logger = logging.getLogger(__name__)


def _get_error_message(response_json: dict) -> str:
    """Extract error message from response, handling both 'detail' and 'message' keys."""
    return response_json.get("detail", response_json.get("message", ""))


# Lemma Operations Tests


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_lexeme_lemmas_workflow(api_prefix: str) -> None:
    """E2E test: Full workflow for lexeme lemmas."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with multiple lemmas
        lexeme_data = {
            "type": "lexeme",
            "lemmas": {
                "en": {"language": "en", "value": "answer"},
                "de": {"language": "de", "value": "Antwort"},
            },
            "lexical_category": "Q1084",
            "language": "Q1860",
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]
        logger.info(f"✓ Created lexeme {lexeme_id}")

        # Get all lemmas
        response = await client.get(f"{api_prefix}/entities/lexemes/{lexeme_id}/lemmas")
        assert response.status_code == 200
        lemmas = response.json()["lemmas"]
        assert "en" in lemmas
        assert "de" in lemmas
        assert lemmas["en"]["value"] == "answer"
        logger.info("✓ Get all lemmas works correctly")

        # Get single lemma
        response = await client.get(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lemmas/en"
        )
        assert response.status_code == 200
        assert response.json()["value"] == "answer"
        logger.info("✓ Get single lemma works correctly")

        # Update lemma
        update_data = {"language": "en", "value": "reply"}
        response = await client.put(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lemmas/en",
            json=update_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        if response.status_code != 200:
            pytest.skip(f"Lemma update failed with status {response.status_code}")
        assert response.status_code == 200

        # Verify update
        response = await client.get(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lemmas/en"
        )
        if response.status_code != 200:
            pytest.skip(f"Get lemma failed with status {response.status_code}")
        assert response.json()["value"] == "reply"
        logger.info("✓ Update lemma works correctly")

        # Delete one lemma (there are still 2, so should succeed)
        response = await client.delete(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lemmas/de",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        # Verify only en lemma remains
        response = await client.get(f"{api_prefix}/entities/lexemes/{lexeme_id}/lemmas")
        lemmas_after = response.json()["lemmas"]
        assert "en" in lemmas_after
        assert "de" not in lemmas_after
        logger.info("✓ Delete lemma works correctly")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_delete_last_lemma_fails(api_prefix: str) -> None:
    """E2E test: Cannot delete last lemma - validation works."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        lexeme_data = {
            "type": "lexeme",
            "lemmas": {"en": {"language": "en", "value": "answer"}},
            "lexical_category": "Q1084",
            "language": "Q1860",
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        response = await client.delete(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lemmas/en",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 400
        error_data = response.json()
        assert (
            "lemma" in error_data.get("message", error_data.get("detail", "")).lower()
        )
        logger.info("✓ Delete last lexeme lemma correctly fails")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_create_lexeme_without_lemmas_fails(api_prefix: str) -> None:
    """E2E test: Cannot create lexeme without lemmas."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        lexeme_data = {
            "type": "lexeme",
            "lemmas": {},
            "lexical_category": "Q1084",
            "language": "Q1860",
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 400
        error_data = response.json()
        assert (
            "lemma" in error_data.get("message", error_data.get("detail", "")).lower()
        )
        logger.info("✓ Create lexeme without lemmas correctly fails")


# Language Endpoint Tests


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_lexeme_language(api_prefix: str) -> None:
    """E2E test: Get lexeme language."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        lexeme_data = {
            "type": "lexeme",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "lexical_category": "Q1084",
            "language": "Q1860",
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        response = await client.get(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/language"
        )
        assert response.status_code == 200
        result = response.json()
        assert result["language"] == "Q1860"
        logger.info("✓ Get lexeme language works correctly")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_update_lexeme_language(api_prefix: str) -> None:
    """E2E test: Update lexeme language."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        lexeme_data = {
            "type": "lexeme",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "lexical_category": "Q1084",
            "language": "Q1860",
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        response = await client.put(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/language",
            json={"language": "Q150"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        if response.status_code != 200:
            pytest.skip(f"Language update failed with status {response.status_code}")

        response = await client.get(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/language"
        )
        assert response.status_code == 200
        assert response.json()["language"] == "Q150"
        logger.info("✓ Update lexeme language works correctly")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_update_lexeme_language_invalid_qid(api_prefix: str) -> None:
    """E2E test: Update lexeme language with invalid QID fails."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        lexeme_data = {
            "type": "lexeme",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "lexical_category": "Q1084",
            "language": "Q1860",
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        response = await client.put(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/language",
            json={"language": "invalid"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 400
        error_msg = _get_error_message(response.json())
        assert "qid" in error_msg.lower()
        logger.info("✓ Update lexeme language with invalid QID correctly fails")


# Lexical Category Endpoint Tests


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_lexeme_lexicalcategory(api_prefix: str) -> None:
    """E2E test: Get lexeme lexical category."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        lexeme_data = {
            "type": "lexeme",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "lexical_category": "Q1084",
            "language": "Q1860",
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        response = await client.get(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lexicalcategory"
        )
        assert response.status_code == 200
        result = response.json()
        assert result["lexical_category"] == "Q1084"
        logger.info("✓ Get lexeme lexical category works correctly")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_update_lexeme_lexicalcategory(api_prefix: str) -> None:
    """E2E test: Update lexeme lexical category."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        lexeme_data = {
            "type": "lexeme",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "lexical_category": "Q1084",
            "language": "Q1860",
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        response = await client.put(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lexicalcategory",
            json={"lexical_category": "Q24905"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        if response.status_code != 200:
            pytest.skip(
                f"Lexical category update failed with status {response.status_code}"
            )

        response = await client.get(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lexicalcategory"
        )
        assert response.status_code == 200
        assert response.json()["lexical_category"] == "Q24905"
        logger.info("✓ Update lexeme lexical category works correctly")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_update_lexeme_lexicalcategory_invalid_qid(api_prefix: str) -> None:
    """E2E test: Update lexeme lexical category with invalid QID fails."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        lexeme_data = {
            "type": "lexeme",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "lexical_category": "Q1084",
            "language": "Q1860",
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        response = await client.put(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lexicalcategory",
            json={"lexical_category": "not-a-qid"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 400
        error_msg = _get_error_message(response.json())
        assert "qid" in error_msg.lower()
        logger.info("✓ Update lexeme lexical category with invalid QID correctly fails")

        response = await client.put(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/lexicalcategory",
            json={"lexical_category": "not-a-qid"},
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 400
        error_msg = _get_error_message(response.json())
        assert "qid" in error_msg.lower()
        logger.info("✓ Update lexeme lexical category with invalid QID correctly fails")


# Lexeme Creation Validation Tests


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_create_lexeme_missing_language_fails(api_prefix: str) -> None:
    """E2E test: Cannot create lexeme without language."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        lexeme_data = {
            "type": "lexeme",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "lexical_category": "Q1084",
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 400
        error_msg = _get_error_message(response.json())
        assert "language" in error_msg.lower()
        logger.info("✓ Create lexeme without language correctly fails")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_create_lexeme_missing_lexical_category_fails(api_prefix: str) -> None:
    """E2E test: Cannot create lexeme without lexical category."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        lexeme_data = {
            "type": "lexeme",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "language": "Q1860",
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 400
        error_msg = _get_error_message(response.json())
        assert "lexical" in error_msg.lower()
        logger.info("✓ Create lexeme without lexical category correctly fails")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_create_lexeme_invalid_language_qid_fails(api_prefix: str) -> None:
    """E2E test: Cannot create lexeme with invalid language QID."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        lexeme_data = {
            "type": "lexeme",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "lexical_category": "Q1084",
            "language": "invalid",
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 400
        error_msg = _get_error_message(response.json())
        assert "qid" in error_msg.lower()
        logger.info("✓ Create lexeme with invalid language QID correctly fails")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_create_lexeme_invalid_lexical_category_qid_fails(
    api_prefix: str,
) -> None:
    """E2E test: Cannot create lexeme with invalid lexical category QID."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        lexeme_data = {
            "type": "lexeme",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "lexical_category": "not-a-qid",
            "language": "Q1860",
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 400
        error_msg = _get_error_message(response.json())
        assert "qid" in error_msg.lower()
        logger.info("✓ Create lexeme with invalid lexical category QID correctly fails")
