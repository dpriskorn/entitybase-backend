"""Integration tests for qualifier deduplication."""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_entity_creation_with_qualifiers_deduplicates(api_prefix: str) -> None:
    """Test that creating an entity with qualifiers in statements stores them as hash references."""
    from models.rest_api.main import app

    statement_claim = {
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
        "qualifiers": {
            "P580": [
                {
                    "snaktype": "value",
                    "property": "P580",
                    "datavalue": {
                        "value": {
                            "time": "+2023-01-01T00:00:00Z",
                            "timezone": 0,
                            "before": 0,
                            "after": 0,
                            "precision": 11,
                            "calendarmodel": "http://www.wikidata.org/entity/Q1985727",
                        },
                        "type": "time",
                    },
                    "datatype": "time",
                }
            ]
        },
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Create empty entity
        response = await client.post(
            f"{api_prefix}/entities/items",
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
        entity_id = response.json()["data"]["entity_id"]

        # Add statement with qualifiers
        response = await client.post(
            f"{api_prefix}/entities/{entity_id}/statements",
            json={"claim": statement_claim},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200

        # Retrieve the entity
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        entity = response.json()

        # Get statement hash and resolve to get statement content
        statement_hash = entity["data"]["revision"]["hashes"]["statements"][0]
        response = await client.get(f"{api_prefix}/resolve/statements/{statement_hash}")
        assert response.status_code == 200
        statement = response.json()[0]

        # Verify qualifiers field is an integer hash, not an object
        assert "qualifiers" in statement
        assert isinstance(statement["qualifiers"], int)
        assert statement["qualifiers"] > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_qualifier_endpoint_single_fetch(api_prefix: str) -> None:
    """Test fetching a single qualifier by hash."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Test fetching qualifier with mock hash
        mock_hash = "123456789"

        response = await client.get(f"{api_prefix}/resolve/qualifiers/{mock_hash}")
        assert response.status_code == 200
        result = response.json()
        # Should return array with one element (null for missing qualifier)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_qualifier_endpoint_batch_fetch(api_prefix: str) -> None:
    """Test fetching multiple qualifiers by hashes."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Test batch fetch with mock hashes
        mock_hashes = "111,222,333"

        response = await client.get(f"{api_prefix}/resolve/qualifiers/{mock_hashes}")
        assert response.status_code == 200
        result = response.json()
        # Should return array with nulls for missing qualifiers
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(item is None for item in result)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_qualifier_endpoint_invalid_hash(api_prefix: str) -> None:
    """Test qualifier endpoint with invalid hash format."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/resolve/qualifiers/invalid-hash")
        assert response.status_code == 400
        error = response.json()
        assert "Invalid hash format" in error["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_qualifier_endpoint_too_many_hashes(api_prefix: str) -> None:
    """Test qualifier endpoint with too many hashes."""
    from models.rest_api.main import app

    # Create 101 mock hashes (exceeds limit of 100)
    mock_hashes = ",".join([f"{i}" for i in range(101)])

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/resolve/qualifiers/{mock_hashes}")
        assert response.status_code == 400
        error = response.json()
        assert "Too many hashes" in error["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_qualifier_endpoint_no_hashes(api_prefix: str) -> None:
    """Test qualifier endpoint with no hashes provided."""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"{api_prefix}/resolve/qualifiers/")
        assert response.status_code == 404

        # Test with empty hash parameter
        response = await client.get(f"{api_prefix}/resolve/qualifiers/,,,")
        assert response.status_code == 400
        error = response.json()
        assert "No hashes provided" in error["message"]
