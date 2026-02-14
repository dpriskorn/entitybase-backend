"""Integration tests for qualifier deduplication."""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_entity_creation_with_qualifiers_deduplicates(api_prefix: str) -> None:
    """Test that creating an entity with qualifiers in statements stores them as hash references."""
    from models.rest_api.main import app

    entity_data = {
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
        entity_response = response.json()
        entity_id = entity_response["id"]

        # Retrieve the entity
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        entity = response.json()

        # Check that the statement has qualifiers
        p31_claims = entity["claims"]["P31"]
        assert len(p31_claims) == 1
        statement = p31_claims[0]

        # Verify qualifiers field is an integer hash, not an object
        assert "qualifiers" in statement
        assert isinstance(statement["qualifiers"], int)
        assert statement["qualifiers"] > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_qualifier_endpoint_single_fetch(api_prefix: str) -> None:
    """Test fetching a single qualifier by hash."""
    from models.rest_api.main import app

    entity_data = {
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
        assert response.status_code == 201
        entity_response = response.json()
        entity_id = entity_response["id"]

        # Retrieve the entity to get qualifier hash
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        entity = response.json()

        # Extract qualifier hash from response
        statement = entity["claims"]["P31"][0]
        qualifier_hash = statement["qualifiers"]
        assert isinstance(qualifier_hash, int)

        # Test fetching qualifier
        response = await client.get(f"{api_prefix}/resolve/qualifiers/{qualifier_hash}")
        assert response.status_code == 200
        result = response.json()
        # Should return array with one element containing qualifier data
        assert isinstance(result, list)
        assert len(result) == 1
        # The qualifier should contain snak structure
        assert result[0] is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_qualifier_endpoint_batch_fetch(api_prefix: str) -> None:
    """Test fetching multiple qualifiers by hashes."""
    from models.rest_api.main import app

    entity_data = {
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
                },
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "value": {
                                "id": "Q6",
                                "entity-type": "item",
                                "numeric-id": 6,
                            },
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {
                        "P582": [
                            {
                                "snaktype": "value",
                                "property": "P582",
                                "datavalue": {
                                    "value": {
                                        "time": "+2024-01-01T00:00:00Z",
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
                },
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "value": {
                                "id": "Q7",
                                "entity-type": "item",
                                "numeric-id": 7,
                            },
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {
                        "P585": [
                            {
                                "snaktype": "value",
                                "property": "P585",
                                "datavalue": {
                                    "value": {
                                        "time": "+2025-01-01T00:00:00Z",
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
                },
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
        assert response.status_code == 201
        entity_response = response.json()
        entity_id = entity_response["id"]

        # Retrieve the entity to get qualifier hashes
        response = await client.get(f"{api_prefix}/entities/{entity_id}")
        assert response.status_code == 200
        entity = response.json()

        # Extract 2-3 different qualifier hashes
        p31_claims = entity["claims"]["P31"]
        qualifier_hashes = [claim["qualifiers"] for claim in p31_claims[:2]]

        # Convert to comma-separated string for batch API call
        hashes_str = ",".join(str(h) for h in qualifier_hashes)

        # Test batch fetch
        response = await client.get(f"{api_prefix}/resolve/qualifiers/{hashes_str}")
        assert response.status_code == 200
        result = response.json()

        # Should return array with qualifier data
        assert isinstance(result, list)
        assert len(result) == 2
        # All qualifiers should be present
        assert all(item is not None for item in result)


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

    # Create 101 hashes (exceeds limit of 100)
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
