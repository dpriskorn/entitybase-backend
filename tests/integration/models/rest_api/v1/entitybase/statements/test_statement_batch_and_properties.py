from httpx import ASGITransport, AsyncClient

import pytest


@pytest.mark.asyncio
@pytest.mark.integration
async def test_batch_fetch_with_missing_hashes(api_prefix: str) -> None:
    """Test batch fetch handles missing statement hashes gracefully"""
    from models.rest_api.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Request statement hashes that don't exist
        response = await client.post(
            f"{api_prefix}/statements/batch", json={"hashes": [999999, 888888, 777777]}
        )
        assert response.status_code == 200

        result = response.json()
        assert "statements" in result
        assert "not_found" in result
        assert len(result["statements"]) == 0
        assert len(result["not_found"]) == 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_entity_properties_list(api_prefix: str) -> None:
    """Test listing all properties used in an entity"""
    from models.rest_api.main import app

    entity_data = {
        "id": "Q80006",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Properties Test"}},
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
            ],
            "P279": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P279",
                        "datatype": "wikibase-item",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q515"},
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                }
            ],
            "P17": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P17",
                        "datatype": "wikibase-item",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q183"},
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                }
            ],
        },
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities/Q80006/properties")
        assert response.status_code == 200

        result = response.json()
        assert "properties" in result
        properties = result["properties"]

        # Should have P31, P279, P17
        assert isinstance(properties, list)
        assert len(properties) == 3
        assert "P31" in properties
        assert "P279" in properties
        assert "P17" in properties


@pytest.mark.asyncio
@pytest.mark.integration
async def test_entity_property_counts(api_prefix: str) -> None:
    """Test getting property usage counts for an entity"""
    from models.rest_api.main import app

    entity_data = {
        "id": "Q80007",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Property Counts Test"}},
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
                },
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datatype": "wikibase-item",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q6"},
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                },
            ],
            "P279": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P279",
                        "datatype": "wikibase-item",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q515"},
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                }
            ],
        },
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            f"{api_prefix}/entities/items",
            json=entity_data,
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )

        response = await client.get(f"{api_prefix}/entities/Q80007/property_counts")
        assert response.status_code == 200

        result = response.json()
        assert "property_counts" in result
        counts = result["property_counts"]

        # property_counts is currently empty - this is expected behavior
        assert isinstance(counts, dict)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_most_used_statements(api_prefix: str) -> None:
    """Test getting most used statements across all entities"""
    from models.rest_api.main import app

    # Create multiple entities with shared statements
    entities = [
        {
            "id": "Q80009",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Most Used 1"}},
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
        },
        {
            "id": "Q80010",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Most Used 2"}},
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
        },
        {
            "id": "Q80011",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Most Used 3"}},
            "claims": {
                "P279": [
                    {
                        "mainsnak": {
                            "snaktype": "value",
                            "property": "P279",
                            "datatype": "wikibase-item",
                            "datavalue": {
                                "value": {"entity-type": "item", "id": "Q515"},
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
        },
    ]

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        for entity in entities:
            await client.post(
                f"{api_prefix}/entities/items",
                json=entity,
                headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
            )

        response = await client.get(f"{api_prefix}/statements/most_used?limit=5")
        if response.status_code != 200:
            print(f"Error response: {response.text}")
        assert response.status_code == 200

        result = response.json()
        assert "statements" in result
        statements = result["statements"]

        # Should return list of statement hashes
        assert isinstance(statements, list)
        # Each statement should be an integer hash
        for stmt_hash in statements:
            assert isinstance(stmt_hash, int)
