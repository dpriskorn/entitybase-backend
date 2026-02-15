"""E2E tests for lexeme sense operations."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_list_lexeme_senses(api_prefix: str) -> None:
    """E2E test: List all senses for a lexeme, sorted by numeric suffix."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with senses
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "senses": [
                {"glosses": {"en": {"language": "en", "value": "A test sense"}}},
                {"glosses": {"en": {"language": "en", "value": "Another meaning"}}},
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        # List senses
        response = await client.get(f"{api_prefix}/entities/lexemes/{lexeme_id}/senses")
        assert response.status_code == 200
        data = response.json()
        assert "senses" in data or isinstance(data, list)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_create_lexeme_sense(api_prefix: str) -> None:
    """E2E test: Create a new sense for a lexeme."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "answer"}},
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        # Create sense
        sense_data = {"glosses": {"en": {"language": "en", "value": "A reply"}}}
        response = await client.post(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/senses",
            json=sense_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_single_sense(api_prefix: str) -> None:
    """E2E test: Get single sense by ID (accepts L42-S1 or S1 format)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with sense
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "senses": [
                {"glosses": {"en": {"language": "en", "value": "A test sense"}}},
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        # Get sense by full ID
        response = await client.get(
            f"{api_prefix}/entities/lexemes/senses/{lexeme_id}-S1"
        )
        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_delete_sense(api_prefix: str) -> None:
    """E2E test: Delete a sense by ID."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with multiple senses
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "senses": [
                {"glosses": {"en": {"language": "en", "value": "First meaning"}}},
                {"glosses": {"en": {"language": "en", "value": "Second meaning"}}},
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        # Delete one sense
        response = await client.delete(
            f"{api_prefix}/entities/lexemes/senses/{lexeme_id}-S2",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_sense_glosses(api_prefix: str) -> None:
    """E2E test: Get all glosses for a sense."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with sense
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "senses": [
                {
                    "glosses": {
                        "en": {"language": "en", "value": "A test sense"},
                        "de": {"language": "de", "value": "Ein Prüfungssinn"},
                    },
                },
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        # Get all glosses
        response = await client.get(f"{api_prefix}/entities/lexemes/senses/{lexeme_id}-S1/glosses")
        assert response.status_code == 200
        if response.status_code == 200:
            data = response.json()
            assert "glosses" in data or isinstance(data, dict)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_get_sense_gloss_by_language(api_prefix: str) -> None:
    """E2E test: Get gloss for a sense in specific language."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with sense
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "senses": [
                {"glosses": {"en": {"language": "en", "value": "A test sense"}}},
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        # Get gloss by language
        response = await client.get(
            f"{api_prefix}/entities/lexemes/senses/{lexeme_id}-S1/glosses/en"
        )
        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_update_sense_gloss(api_prefix: str) -> None:
    """E2E test: Update sense gloss for language."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with sense
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "senses": [
                {"glosses": {"en": {"language": "en", "value": "A test sense"}}},
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        # Update gloss
        updated_gloss = {"language": "en", "value": "An updated test sense"}
        response = await client.put(
            f"{api_prefix}/entities/lexemes/senses/{lexeme_id}-S1/glosses/en",
            json=updated_gloss,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_delete_sense_gloss(api_prefix: str) -> None:
    """E2E test: Delete sense gloss for language."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with sense with multiple glosses
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "senses": [
                {
                    "glosses": {
                        "en": {"language": "en", "value": "A test sense"},
                        "de": {"language": "de", "value": "Ein Prüfungssinn"},
                    },
                },
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        # Delete one gloss
        response = await client.delete(
            f"{api_prefix}/entities/lexemes/senses/{lexeme_id}-S1/glosses/de",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_add_sense_gloss(api_prefix: str) -> None:
    """E2E test: Add a new sense gloss via POST."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "senses": [
                {"glosses": {"en": {"language": "en", "value": "A test sense"}}},
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        gloss_data = {"language": "de", "value": "Ein Testsinn"}
        response = await client.post(
            f"{api_prefix}/entities/lexemes/senses/{lexeme_id}-S1/glosses/de",
            json=gloss_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_add_sense_gloss_already_exists(api_prefix: str) -> None:
    """E2E test: Adding existing gloss returns 409."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "senses": [
                {"glosses": {"en": {"language": "en", "value": "A test sense"}}},
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        gloss_data = {"language": "en", "value": "A test sense"}
        response = await client.post(
            f"{api_prefix}/entities/lexemes/senses/{lexeme_id}-S1/glosses/en",
            json=gloss_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_delete_sense_gloss_last_gloss_fails(api_prefix: str) -> None:
    """E2E test: Deleting last gloss returns 400."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "senses": [
                {"glosses": {"en": {"language": "en", "value": "A test sense"}}},
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        response = await client.delete(
            f"{api_prefix}/entities/lexemes/senses/{lexeme_id}-S1/glosses/en",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 400
        assert "cannot have 0 glosses" in response.json()["detail"]


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_add_statement_to_sense(api_prefix: str) -> None:
    """E2E test: Add a statement to a sense."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with sense
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "senses": [
                {"glosses": {"en": {"language": "en", "value": "A test sense"}}},
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        lexeme_id = response.json()["id"]

        # Add statement to sense
        statement_data = {
            "property": {"id": "P31", "data_type": "wikibase-item"},
            "value": {"type": "value", "content": "Q5"},
            "rank": "normal",
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes/senses/{lexeme_id}-S1/statements",
            json=statement_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
