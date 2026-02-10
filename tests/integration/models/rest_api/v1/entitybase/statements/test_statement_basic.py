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
        response = await client.post(f"{api_prefix}/entities/", json=entity_data)
        assert response.status_code == 200

        # Get entity
        entity_response = await client.get(f"{api_prefix}/entities/Q80005")
        assert entity_response.status_code == 200
        entity = entity_response.json()

        assert "statements" in entity
        assert len(entity["statements"]) == 1
        assert isinstance(entity["statements"][0], int)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_invalid_statement_rejected(api_prefix: str) -> None:
    """Test that invalid statements are rejected"""
    from models.rest_api.main import app

    entity_data = {
        "id": "Q80006",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Invalid Statement"}},
        "claims": {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datatype": "invalid-datatype",
                        "datavalue": {
                            "value": "invalid",
                            "type": "invalid-type",
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
        response = await client.post(f"{api_prefix}/entities/", json=entity_data)
        assert response.status_code == 400
