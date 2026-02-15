import logging

import pytest
from httpx import ASGITransport, AsyncClient

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_sense_gloss() -> None:
    """Integration test: Add a new sense gloss via POST."""
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
        create_response = await client.post(
            "/v1/entitybase/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        lexeme_id = create_response.json()["id"]

        gloss_data = {"language": "de", "value": "Ein Testsinn"}
        response = await client.post(
            f"/v1/entitybase/entities/lexemes/senses/{lexeme_id}-S1/glosses/de",
            json=gloss_data,
            headers={"X-Edit-Summary": "add gloss", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        logger.info("✓ POST sense gloss passed")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_sense_gloss_already_exists() -> None:
    """Integration test: Adding existing gloss returns 409."""
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
        create_response = await client.post(
            "/v1/entitybase/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        lexeme_id = create_response.json()["id"]

        gloss_data = {"language": "en", "value": "A test sense"}
        response = await client.post(
            f"/v1/entitybase/entities/lexemes/senses/{lexeme_id}-S1/glosses/en",
            json=gloss_data,
            headers={"X-Edit-Summary": "add gloss", "X-User-ID": "0"},
        )
        assert response.status_code == 409
        assert "already exists" in response.json()["message"]
        logger.info("✓ POST sense gloss already exists passed")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_sense_gloss() -> None:
    """Integration test: Update existing sense gloss via PUT."""
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
        create_response = await client.post(
            "/v1/entitybase/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        lexeme_id = create_response.json()["id"]

        gloss_data = {"language": "en", "value": "Updated sense"}
        response = await client.put(
            f"/v1/entitybase/entities/lexemes/senses/{lexeme_id}-S1/glosses/en",
            json=gloss_data,
            headers={"X-Edit-Summary": "update gloss", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        logger.info("✓ PUT sense gloss passed")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_sense_gloss() -> None:
    """Integration test: Delete sense gloss."""
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
                {
                    "glosses": {
                        "en": {"language": "en", "value": "A test sense"},
                        "de": {"language": "de", "value": "Ein Testsinn"},
                    },
                },
            ],
        }
        create_response = await client.post(
            "/v1/entitybase/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        lexeme_id = create_response.json()["id"]

        response = await client.delete(
            f"/v1/entitybase/entities/lexemes/senses/{lexeme_id}-S1/glosses/de",
            headers={"X-Edit-Summary": "delete gloss", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        logger.info("✓ DELETE sense gloss passed")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_sense_gloss_last_gloss_fails() -> None:
    """Integration test: Deleting last gloss returns 400."""
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
        create_response = await client.post(
            "/v1/entitybase/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        lexeme_id = create_response.json()["id"]

        response = await client.delete(
            f"/v1/entitybase/entities/lexemes/senses/{lexeme_id}-S1/glosses/en",
            headers={"X-Edit-Summary": "delete gloss", "X-User-ID": "0"},
        )
        assert response.status_code == 400
        assert "cannot have 0 glosses" in response.json()["message"]
        logger.info("✓ DELETE last gloss fails passed")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_sense_glosses() -> None:
    """Integration test: Get all glosses for a sense."""
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
                {
                    "glosses": {
                        "en": {"language": "en", "value": "A test sense"},
                        "de": {"language": "de", "value": "Ein Testsinn"},
                    },
                },
            ],
        }
        create_response = await client.post(
            "/v1/entitybase/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        lexeme_id = create_response.json()["id"]

        response = await client.get(
            f"/v1/entitybase/entities/lexemes/senses/{lexeme_id}-S1/glosses",
        )
        assert response.status_code == 200
        data = response.json()
        assert "glosses" in data
        logger.info("✓ GET sense glosses passed")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_sense_gloss_by_language() -> None:
    """Integration test: Get gloss for a sense in specific language."""
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
        create_response = await client.post(
            "/v1/entitybase/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert create_response.status_code == 200
        lexeme_id = create_response.json()["id"]

        response = await client.get(
            f"/v1/entitybase/entities/lexemes/senses/{lexeme_id}-S1/glosses/en",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == "A test sense"
        logger.info("✓ GET sense gloss by language passed")
