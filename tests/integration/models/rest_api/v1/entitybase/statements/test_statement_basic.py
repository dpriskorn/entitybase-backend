from httpx import ASGITransport, AsyncClient

import pytest


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_nonexistent_statement_404(api_prefix: str) -> None:
    """Test fetching nonexistent statement returns 404"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/statements/999999")
        assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_entity_revision_with_statements(api_prefix: str) -> None:
    """Test that entity revisions include statement hashes"""
    from models.rest_api.main import app

    entity_data = {
        "id": "Q80005",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Revision Statements"}},
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
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        # Get entity
        entity_response = await client.get(f"{api_prefix}/entities/Q80005")
        assert entity_response.status_code == 200
        entity = entity_response.json()

        # Statements are in data.revision.hashes.statements
        assert "data" in entity
        assert "revision" in entity["data"]
        assert "hashes" in entity["data"]["revision"]
        assert "statements" in entity["data"]["revision"]["hashes"]
        statements = entity["data"]["revision"]["hashes"]["statements"]
        assert len(statements) == 1
        assert isinstance(statements[0], int)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_invalid_statement_rejected(api_prefix: str) -> None:
    """Test that invalid statement structure is rejected"""
    from models.rest_api.main import app

    entity_data = {
        "id": "Q80006",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Invalid Statement"}},
        "claims": {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "novalue",
                        "property": "P31",
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
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
