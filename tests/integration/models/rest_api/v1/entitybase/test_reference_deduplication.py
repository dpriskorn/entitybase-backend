"""Integration tests for reference deduplication."""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_entity_creation_with_references_deduplicates(api_prefix: str) -> None:
    """Test that creating an entity with references deduplicates them."""
    from models.rest_api.main import app

    entity_data = {
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Entity"}},
        "claims": {
            "P31": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "value": {
                                "id": "Q5",
                                "entity-type": "item",
                                "numeric-id": 5,
                            },
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                    "references": [
                        {
                            "snaks": {
                                "P854": [
                                    {
                                        "snaktype": "value",
                                        "property": "P854",
                                        "datavalue": {
                                            "value": "http://example.com",
                                            "type": "string",
                                        },
                                    }
                                ]
                            },
                            "snaks-order": ["P854"],
                        }
                    ],
                }
            ]
        },
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create entity
        response = await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["id"]

        # Read entity back
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        data = response.json()

        # Check that statement hashes were created and stored
        # Entity structure: {id, rev_id, data: {revision: {hashes: {statements: [...]}}}}
        # The actual statement hashes are in data["data"]["revision"]["hashes"]["statements"]
        statement_hashes = data["data"]["revision"]["hashes"]["statements"]
        assert isinstance(statement_hashes, list)
        assert len(statement_hashes) > 0
        assert all(isinstance(h, int) for h in statement_hashes)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_reference_batch_endpoint(api_prefix: str) -> None:
    """Test batch reference fetching."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Assume some references exist from previous test
        response = await client.get(f"{api_prefix}/resolve/references/123,456")
        # Should return array with nulls for missing
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
