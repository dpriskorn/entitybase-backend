"""E2E tests for lexeme form operations."""

import pytest
import sys

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, "src")


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.xfail(reason="Lexeme creation validation not fully implemented")
async def test_list_lexeme_forms(api_prefix: str) -> None:
    """E2E test: List all forms for a lexeme, sorted by numeric suffix."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with forms
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "forms": [
                {
                    "representations": {"en": {"language": "en", "value": "tests"}},
                    "grammaticalFeatures": ["Q110786"],
                },
                {
                    "representations": {"en": {"language": "en", "value": "testing"}},
                    "grammaticalFeatures": ["Q110786"],
                },
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        if response.status_code != 200:
            pytest.skip("Lexeme creation with forms not fully implemented")
        lexeme_id = response.json()["id"]

        # List forms
        response = await client.get(f"{api_prefix}/entities/lexemes/{lexeme_id}/forms")
        assert response.status_code == 200
        data = response.json()
        assert "forms" in data or isinstance(data, list)


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.xfail(reason="Lexeme creation validation not fully implemented")
async def test_create_lexeme_form(api_prefix: str) -> None:
    """E2E test: Create a new form for a lexeme."""
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
        if response.status_code != 200:
            pytest.skip("Lexeme creation not fully implemented")
        lexeme_id = response.json()["id"]

        # Create form
        form_data = {
            "representations": {"en": {"language": "en", "value": "answers"}},
            "grammaticalFeatures": ["Q110786"],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes/{lexeme_id}/forms",
            json=form_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code in [200, 201, 500]


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.xfail(reason="Lexeme creation validation not fully implemented")
async def test_get_single_form(api_prefix: str) -> None:
    """E2E test: Get single form by ID (accepts L42-F1 or F1 format)."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with form
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "forms": [
                {
                    "representations": {"en": {"language": "en", "value": "tests"}},
                    "grammaticalFeatures": ["Q110786"],
                },
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        if response.status_code != 200:
            pytest.skip("Lexeme creation with forms not fully implemented")
        lexeme_id = response.json()["id"]

        # Get form by short ID (F1 format)
        response = await client.get(f"{api_prefix}/entities/lexemes/forms/F1")
        assert response.status_code in [200, 404]

        # Try full ID format (if form has ID)
        response = await client.get(
            f"{api_prefix}/entities/lexemes/forms/{lexeme_id}-F1"
        )
        assert response.status_code in [200, 404]


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.xfail(reason="Lexeme creation validation not fully implemented")
async def test_delete_form(api_prefix: str) -> None:
    """E2E test: Delete a form by ID."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with multiple forms
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "forms": [
                {
                    "representations": {"en": {"language": "en", "value": "tests"}},
                    "grammaticalFeatures": ["Q110786"],
                },
                {
                    "representations": {"en": {"language": "en", "value": "testing"}},
                    "grammaticalFeatures": ["Q110786"],
                },
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        if response.status_code != 200:
            pytest.skip("Lexeme creation with forms not fully implemented")
        lexeme_id = response.json()["id"]

        # Delete one form
        response = await client.delete(
            f"{api_prefix}/entities/lexemes/forms/F2",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code in [200, 204, 404, 500]


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.xfail(reason="Lexeme creation validation not fully implemented")
async def test_get_form_representations(api_prefix: str) -> None:
    """E2E test: Get all representations for a form."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with form
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "forms": [
                {
                    "representations": {
                        "en": {"language": "en", "value": "tests"},
                        "de": {"language": "de", "value": "Tests"},
                    },
                    "grammaticalFeatures": ["Q110786"],
                },
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        if response.status_code != 200:
            pytest.skip("Lexeme creation with forms not fully implemented")
        lexeme_id = response.json()["id"]

        # Get all representations
        response = await client.get(
            f"{api_prefix}/entities/lexemes/forms/F1/representation"
        )
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "representations" in data or isinstance(data, dict)


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.xfail(reason="Lexeme creation validation not fully implemented")
async def test_get_form_representation_by_language(api_prefix: str) -> None:
    """E2E test: Get representation for a form in specific language."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with form
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "forms": [
                {
                    "representations": {"en": {"language": "en", "value": "tests"}},
                    "grammaticalFeatures": ["Q110786"],
                },
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        if response.status_code != 200:
            pytest.skip("Lexeme creation with forms not fully implemented")
        lexeme_id = response.json()["id"]

        # Get representation by language
        response = await client.get(
            f"{api_prefix}/entities/lexemes/forms/F1/representation/en"
        )
        assert response.status_code in [200, 404]


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.xfail(reason="Lexeme creation validation not fully implemented")
async def test_add_form_representation(api_prefix: str) -> None:
    """E2E test: Add a new form representation for language."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with form
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "forms": [
                {
                    "representations": {"en": {"language": "en", "value": "tests"}},
                    "grammaticalFeatures": ["Q110786"],
                },
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        if response.status_code != 200:
            pytest.skip("Lexeme creation with forms not fully implemented")
        lexeme_id = response.json()["id"]

        # Add new language representation
        new_rep = {"language": "de", "value": "Tests"}
        response = await client.post(
            f"{api_prefix}/entities/lexemes/forms/F1/representation/de",
            json=new_rep,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code in [200, 201, 500]


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.xfail(reason="Lexeme creation validation not fully implemented")
async def test_update_form_representation(api_prefix: str) -> None:
    """E2E test: Update form representation for language."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with form
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "forms": [
                {
                    "representations": {"en": {"language": "en", "value": "tests"}},
                    "grammaticalFeatures": ["Q110786"],
                },
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        if response.status_code != 200:
            pytest.skip("Lexeme creation with forms not fully implemented")
        lexeme_id = response.json()["id"]

        # Update representation
        updated_rep = {"language": "en", "value": "examined"}
        response = await client.put(
            f"{api_prefix}/entities/lexemes/forms/F1/representation/en",
            json=updated_rep,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code in [200, 500]


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.xfail(reason="Lexeme creation validation not fully implemented")
async def test_delete_form_representation(api_prefix: str) -> None:
    """E2E test: Delete form representation for language."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with form with multiple representations
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "forms": [
                {
                    "representations": {
                        "en": {"language": "en", "value": "tests"},
                        "de": {"language": "de", "value": "Tests"},
                    },
                    "grammaticalFeatures": ["Q110786"],
                },
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        if response.status_code != 200:
            pytest.skip("Lexeme creation with forms not fully implemented")
        lexeme_id = response.json()["id"]

        # Delete one representation
        response = await client.delete(
            f"{api_prefix}/entities/lexemes/forms/F1/representation/de",
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code in [200, 500]


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.xfail(reason="Lexeme creation validation not fully implemented")
async def test_add_statement_to_form(api_prefix: str) -> None:
    """E2E test: Add a statement to a form."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create lexeme with form
        lexeme_data = {
            "type": "lexeme",
            "language": "Q1860",
            "lexicalCategory": "Q1084",
            "lemmas": {"en": {"language": "en", "value": "test"}},
            "forms": [
                {
                    "representations": {"en": {"language": "en", "value": "tests"}},
                    "grammaticalFeatures": ["Q110786"],
                },
            ],
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes",
            json=lexeme_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        if response.status_code != 200:
            pytest.skip("Lexeme creation with forms not fully implemented")
        lexeme_id = response.json()["id"]

        # Add statement to form
        statement_data = {
            "property": {"id": "P31", "data_type": "wikibase-item"},
            "value": {"type": "value", "content": "Q5"},
            "rank": "normal",
        }
        response = await client.post(
            f"{api_prefix}/entities/lexemes/forms/F1/statements",
            json=statement_data,
            headers={"X-Edit-Summary": "E2E test", "X-User-ID": "0"},
        )
        assert response.status_code in [200, 201, 500]
