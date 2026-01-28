import logging
import requests


def test_batch_fetch_with_missing_hashes(
    api_client: requests.Session, base_url: str
) -> None:
    """Test batch fetch handles missing statement hashes gracefully"""
    response = api_client.post(
        f"{base_url}/statements/batch", json={"hashes": [1, 999999, 2]}
    )
    assert response.status_code == 200

    result = response.json()
    assert "statements" in result
    assert "not_found" in result
    assert len(result["not_found"]) == 1
    assert 999999 in result["not_found"]


def test_entity_properties_list(api_client: requests.Session, base_url: str) -> None:
    """Test listing all properties used in an entity"""
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

    api_client.post(f"{base_url}/entity", json=entity_data)

    response = api_client.get(f"{base_url}/entity/Q80006/properties")
    assert response.status_code == 200

    result = response.json()
    assert "properties" in result
    properties = result["properties"]

    # Should have P31, P279, P17
    assert len(properties) == 3
    assert "P31" in properties
    assert "P279" in properties
    assert "P17" in properties

    # Each property should have statement count
    for prop in properties.values():
        assert "count" in prop
        assert isinstance(prop["count"], int)
        assert prop["count"] > 0


def test_entity_property_counts(api_client: requests.Session, base_url: str) -> None:
    """Test getting property usage counts for an entity"""
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

    api_client.post(f"{base_url}/entity", json=entity_data)

    response = api_client.get(f"{base_url}/entity/Q80007/property_counts")
    assert response.status_code == 200

    result = response.json()
    assert "property_counts" in result
    counts = result["property_counts"]

    # P31 should have 2 statements, P279 should have 1
    assert counts["P31"] == 2
    assert counts["P279"] == 1


def test_most_used_statements(api_client: requests.Session, base_url: str) -> None:
    """Test getting most used statements across all entities"""
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

    for entity in entities:
        api_client.post(f"{base_url}/entity", json=entity)

    response = api_client.get(f"{base_url}/statements/most_used?limit=5")
    assert response.status_code == 200

    result = response.json()
    assert "statements" in result
    statements = result["statements"]

    # Should have at least 2 different statements
    assert len(statements) >= 2

    # P31 should be most used (used in 2 entities)
    p31_found = any(s["statement"]["property"] == "P31" for s in statements)
    assert p31_found, "P31 should be in most used statements"

    # Check structure
    for stmt in statements:
        assert "statement" in stmt
        assert "usage_count" in stmt
        assert stmt["usage_count"] > 0
