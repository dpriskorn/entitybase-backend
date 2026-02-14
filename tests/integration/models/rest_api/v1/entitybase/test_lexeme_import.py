"""Integration tests for lexeme import via /import endpoint."""

import json
import pytest
import time
from httpx import ASGITransport, AsyncClient

from models.data.rest_api.v1.entitybase.request import EntityCreateRequest


_lexeme_id_counter = 0


def get_unique_lexeme_id():
    """Generate a unique lexeme ID for testing."""
    global _lexeme_id_counter
    _lexeme_id_counter += 1
    return f"L9999{_lexeme_id_counter}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_lexeme_import_with_lemmas() -> None:
    """Test that lexeme import works with lemmas field."""
    from models.rest_api.main import app

    lexeme_id = get_unique_lexeme_id()
    form_id = f"{lexeme_id}-F1"
    sense_id = f"{lexeme_id}-S1"

    lexeme_data = {
        "id": lexeme_id,
        "type": "lexeme",
        "language": "Q1860",
        "lexical_category": "Q1084",
        "lemmas": {"en": {"language": "en", "value": "answer"}},
        "labels": {"en": {"language": "en", "value": "answer"}},
        "forms": [
            {
                "id": form_id,
                "representations": {"en": {"language": "en", "value": "answer"}},
                "grammaticalFeatures": ["Q110786"],
            }
        ],
        "senses": [
            {
                "id": sense_id,
                "glosses": {"en": {"language": "en", "value": "reply to a question"}},
            }
        ],
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/v1/entitybase/import",
            json=lexeme_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        result = response.json()
        assert result["id"] == lexeme_id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_lexeme_import_without_lemmas_fails() -> None:
    """Test that lexeme import fails without lemmas field."""
    from models.rest_api.main import app

    lexeme_id = get_unique_lexeme_id()
    lexeme_data = {
        "id": lexeme_id,
        "type": "lexeme",
        "language": "Q1860",
        "lexical_category": "Q1084",
        "labels": {"en": {"language": "en", "value": "test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/v1/entitybase/import",
            json=lexeme_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 400
        result = response.json()
        assert "lemma" in str(result.get("message", "")).lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_lexeme_import_preserves_wikidata_id() -> None:
    """Test that lexeme import preserves Wikidata L-prefixed ID."""
    from models.rest_api.main import app

    lexeme_id = get_unique_lexeme_id()
    lexeme_data = {
        "id": lexeme_id,
        "type": "lexeme",
        "language": "Q1860",
        "lexical_category": "Q1084",
        "lemmas": {"en": {"language": "en", "value": "test"}},
        "labels": {"en": {"language": "en", "value": "test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/v1/entitybase/import",
            json=lexeme_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        result = response.json()
        assert result["id"] == lexeme_id


# Language Endpoint Integration Tests


@pytest.mark.asyncio
@pytest.mark.integration
async def test_lexeme_language_get_after_creation() -> None:
    """Test that language can be retrieved after lexeme creation."""
    from models.rest_api.main import app

    lexeme_id = get_unique_lexeme_id()
    lexeme_data = {
        "id": lexeme_id,
        "type": "lexeme",
        "language": "Q1860",
        "lexical_category": "Q1084",
        "lemmas": {"en": {"language": "en", "value": "test"}},
        "labels": {"en": {"language": "en", "value": "test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/v1/entitybase/import",
            json=lexeme_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(
            f"/v1/entitybase/entities/lexemes/{lexeme_id}/language"
        )
        assert response.status_code == 200
        result = response.json()
        assert result["language"] == "Q1860"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_lexeme_lexicalcategory_get_after_creation() -> None:
    """Test that lexical category can be retrieved after lexeme creation."""
    from models.rest_api.main import app

    lexeme_id = get_unique_lexeme_id()
    lexeme_data = {
        "id": lexeme_id,
        "type": "lexeme",
        "language": "Q1860",
        "lexical_category": "Q1084",
        "lemmas": {"en": {"language": "en", "value": "test"}},
        "labels": {"en": {"language": "en", "value": "test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/v1/entitybase/import",
            json=lexeme_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.get(
            f"/v1/entitybase/entities/lexemes/{lexeme_id}/lexicalcategory"
        )
        assert response.status_code == 200
        result = response.json()
        assert result["lexical_category"] == "Q1084"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_lexeme_language_update_invalid_qid_fails() -> None:
    """Test that language update with invalid QID fails."""
    from models.rest_api.main import app

    lexeme_id = get_unique_lexeme_id()
    lexeme_data = {
        "id": lexeme_id,
        "type": "lexeme",
        "language": "Q1860",
        "lexical_category": "Q1084",
        "lemmas": {"en": {"language": "en", "value": "test"}},
        "labels": {"en": {"language": "en", "value": "test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/v1/entitybase/import",
            json=lexeme_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.put(
            f"/v1/entitybase/entities/lexemes/{lexeme_id}/language",
            json={"language": "invalid-qid"},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 400
        error_msg = response.json().get("detail", response.json().get("message", ""))
        assert "qid" in error_msg.lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_lexeme_lexicalcategory_update_invalid_qid_fails() -> None:
    """Test that lexical category update with invalid QID fails."""
    from models.rest_api.main import app

    lexeme_id = get_unique_lexeme_id()
    lexeme_data = {
        "id": lexeme_id,
        "type": "lexeme",
        "language": "Q1860",
        "lexical_category": "Q1084",
        "lemmas": {"en": {"language": "en", "value": "test"}},
        "labels": {"en": {"language": "en", "value": "test"}},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/v1/entitybase/import",
            json=lexeme_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        response = await client.put(
            f"/v1/entitybase/entities/lexemes/{lexeme_id}/lexicalcategory",
            json={"lexical_category": "not-valid"},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 400
        error_msg = response.json().get("detail", response.json().get("message", ""))
        assert "qid" in error_msg.lower()
