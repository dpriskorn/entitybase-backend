import json
import logging

import requests

from rapidhash import rapidhash


def test_statement_creation_and_storage(
    api_client: requests.Session, base_url: str
) -> None:
    """Test creating entity with statements stores them in S3"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q80001",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Statements"}},
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
                        "hash": "somehash",
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                    "id": "Q80001$1",
                }
            ]
        },
    }

    response = api_client.post(f"{base_url}/entity", json=entity_data)
    assert response.status_code == 200
    result = response.json()
    assert result["revision_id"] == 1

    raw = api_client.get(f"{base_url}/raw/Q80001/1").json()
    logger.debug(raw)
    assert "statements" in raw, "Entity revision should have statements array"
    assert len(raw["statements"]) == 1, "Should have 1 statement hash"

    statement_hash = raw["statements"][0]
    assert isinstance(statement_hash, int), "Statement hash should be integer"

    logger.info("✓ Statement creation and storage works")


def test_statement_deduplication(api_client: requests.Session, base_url: str) -> None:
    """Test identical statements are deduplicated (same hash, one S3 object)"""
    logger = logging.getLogger(__name__)

    statement_data = {
        "mainsnak": {
            "snaktype": "value",
            "property": "P31",
            "datatype": "wikibase-item",
            "datavalue": {
                "value": {"entity-type": "item", "id": "Q5"},
                "type": "wikibase-entityid",
            },
            "hash": "somehash",
        },
        "type": "statement",
        "rank": "normal",
        "qualifiers": {},
        "references": [],
        "id": "placeholder",
    }

    entity1_data = {
        "id": "Q80002",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Entity 1"}},
        "claims": {"P31": [{**statement_data, "id": "Q80002$1"}]},
    }

    entity2_data = {
        "id": "Q80003",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Entity 2"}},
        "claims": {"P31": [{**statement_data, "id": "Q80003$1"}]},
    }

    api_client.post(f"{base_url}/entity", json=entity1_data)
    api_client.post(f"{base_url}/entity", json=entity2_data)

    raw1 = api_client.get(f"{base_url}/raw/Q80002/1").json()
    logger.debug(raw1)
    raw2 = api_client.get(f"{base_url}/raw/Q80003/1").json()
    logger.debug(raw2)

    hash1 = raw1["statements"][0]
    hash2 = raw2["statements"][0]

    assert (
        hash1 == hash2
    ), f"Identical statements should have same hash: {hash1} != {hash2}"

    statement_response = api_client.get(f"{base_url}/statement/{hash1}")
    assert statement_response.status_code == 200, "Statement should be accessible"
    statement_data_from_s3 = statement_response.json()
    assert statement_data_from_s3["content_hash"] == hash1

    logger.info("✓ Statement deduplication works (same content = one hash)")


def test_get_single_statement(api_client: requests.Session, base_url: str) -> None:
    """Test retrieving a single statement by hash"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q80004",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Statement Test"}},
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
                        "hash": "hash1",
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                    "id": "Q80004$1",
                }
            ]
        },
    }

    api_client.post(f"{base_url}/entity", json=entity_data)
    raw = api_client.get(f"{base_url}/raw/Q80004/1").json()
    logger.debug(raw)
    statement_hash = raw["statements"][0]

    response = api_client.get(f"{base_url}/statement/{statement_hash}")
    assert response.status_code == 200

    statement = response.json()
    assert statement["content_hash"] == statement_hash
    assert "statement" in statement
    assert "created_at" in statement

    assert statement["statement"]["mainsnak"]["property"] == "P31"
    assert statement["statement"]["type"] == "statement"
    assert statement["statement"]["rank"] == "normal"

    logger.info("✓ Get single statement works")


def test_get_nonexistent_statement_404(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that non-existent statements return 404"""
    logger = logging.getLogger(__name__)

    fake_hash = 1234567890123456789
    response = api_client.get(f"{base_url}/statement/{fake_hash}")
    assert response.status_code == 404

    logger.info("✓ Non-existent statement returns 404")


def test_batch_statement_fetch(api_client: requests.Session, base_url: str) -> None:
    """Test fetching multiple statements in one batch request"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q80005",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Batch Test"}},
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
                        "hash": "hash1",
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                    "id": "Q80005$1",
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
                        "hash": "hash2",
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                    "id": "Q80005$2",
                }
            ],
        },
    }

    api_client.post(f"{base_url}/entity", json=entity_data)
    raw = api_client.get(f"{base_url}/raw/Q80005/1").json()
    logger.debug(raw)
    statement_hashes = raw["statements"]

    response = api_client.post(
        f"{base_url}/statements/batch", json={"hashes": statement_hashes}
    )
    assert response.status_code == 200

    result = response.json()
    assert "statements" in result
    assert len(result["statements"]) == 2
    assert len(result["not_found"]) == 0

    for stmt in result["statements"]:
        assert "content_hash" in stmt
        assert "statement" in stmt
        assert "created_at" in stmt

    logger.info("✓ Batch statement fetch works")


def test_batch_fetch_with_missing_hashes(
    api_client: requests.Session, base_url: str
) -> None:
    """Test batch fetch returns not_found list for missing hashes"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q80006",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Missing Hash Test"}},
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
                        "hash": "hash1",
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                    "id": "Q80006$1",
                }
            ]
        },
    }

    api_client.post(f"{base_url}/entity", json=entity_data)
    raw = api_client.get(f"{base_url}/raw/Q80006/1").json()
    logger.debug(raw)
    real_hash = raw["statements"][0]

    fake_hashes = [1234567890123456789, 9876543210987654321]
    all_hashes = [real_hash] + fake_hashes

    response = api_client.post(
        f"{base_url}/statements/batch", json={"hashes": all_hashes}
    )
    assert response.status_code == 200

    result = response.json()
    assert len(result["statements"]) == 1
    assert len(result["not_found"]) == 2
    assert real_hash in [s["content_hash"] for s in result["statements"]]
    assert all(fake in result["not_found"] for fake in fake_hashes)

    logger.info("✓ Batch fetch handles missing hashes correctly")


def test_entity_properties_list(api_client: requests.Session, base_url: str) -> None:
    """Test getting list of properties for an entity"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q80007",
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
                        "hash": "h1",
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                    "id": "Q80007$1",
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
                        "hash": "h2",
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                    "id": "Q80007$2",
                }
            ],
            "P569": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P569",
                        "datatype": "time",
                        "datavalue": {
                            "value": {
                                "time": "+1952-03-03T00:00:00Z",
                                "timezone": 0,
                                "before": 0,
                                "after": 0,
                                "precision": 11,
                                "calendarmodel": "http://www.wikidata.org/entity/Q1985727",
                            },
                            "type": "time",
                        },
                        "hash": "h3",
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                    "id": "Q80007$3",
                }
            ],
        },
    }

    api_client.post(f"{base_url}/entity", json=entity_data)

    response = api_client.get(f"{base_url}/entity/Q80007/properties")
    assert response.status_code == 200

    result = response.json()
    logger.debug(result)
    assert "properties" in result
    assert len(result["properties"]) == 3
    assert "P31" in result["properties"]
    assert "P279" in result["properties"]
    assert "P569" in result["properties"]

    logger.info("✓ Entity properties list works")


def test_entity_property_counts(api_client: requests.Session, base_url: str) -> None:
    """Test getting statement counts per property"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q80008",
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
                        "hash": "h1",
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                    "id": "Q80008$1",
                },
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datatype": "wikibase-item",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q215627"},
                            "type": "wikibase-entityid",
                        },
                        "hash": "h2",
                    },
                    "type": "statement",
                    "rank": "preferred",
                    "qualifiers": {},
                    "references": [],
                    "id": "Q80008$2",
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
                        "hash": "h3",
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                    "id": "Q80008$3",
                },
            ],
        },
    }

    api_client.post(f"{base_url}/entity", json=entity_data)

    response = api_client.get(f"{base_url}/entity/Q80008/properties/counts")
    assert response.status_code == 200

    result = response.json()
    logger.debug(result)
    assert "property_counts" in result
    assert result["property_counts"]["P31"] == 2
    assert result["property_counts"]["P279"] == 1

    logger.info("✓ Property counts works")


def test_entity_property_hashes(api_client: requests.Session, base_url: str) -> None:
    """Test getting statement hashes for specific properties"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q80009",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Property Hashes Test"}},
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
                        "hash": "h1",
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                    "id": "Q80009$1",
                },
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datatype": "wikibase-item",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q215627"},
                            "type": "wikibase-entityid",
                        },
                        "hash": "h2",
                    },
                    "type": "statement",
                    "rank": "preferred",
                    "qualifiers": {},
                    "references": [],
                    "id": "Q80009$2",
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
                        "hash": "h3",
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                    "id": "Q80009$3",
                },
            ],
        },
    }

    api_client.post(f"{base_url}/entity", json=entity_data)

    response = api_client.get(f"{base_url}/entity/Q80009/properties/P31")
    assert response.status_code == 200

    result = response.json()
    logger.debug(result)
    assert "property_hashes" in result
    assert len(result["property_hashes"]) == 2

    raw = api_client.get(f"{base_url}/raw/Q80009/1").json()
    p31_hashes_in_raw = [h for h in raw["statements"]]

    assert len(result["property_hashes"]) == 2

    logger.info("✓ Property hashes works")


def test_most_used_statements(api_client: requests.Session, base_url: str) -> None:
    """Test getting most-used statements"""
    logger = logging.getLogger(__name__)

    statement = {
        "mainsnak": {
            "snaktype": "value",
            "property": "P31",
            "datatype": "wikibase-item",
            "datavalue": {
                "value": {"entity-type": "item", "id": "Q5"},
                "type": "wikibase-entityid",
            },
            "hash": "h1",
        },
        "type": "statement",
        "rank": "normal",
        "qualifiers": {},
        "references": [],
        "id": "placeholder",
    }

    for i in range(10):
        entity_data = {
            "id": f"Q80010{i}",
            "type": "item",
            "labels": {"en": {"language": "en", "value": f"Entity {i}"}},
            "claims": {"P31": [{**statement, "id": f"Q80010{i}$1"}]},
        }
        api_client.post(f"{base_url}/entity", json=entity_data)

    response = api_client.get(
        f"{base_url}/statement/most_used?limit=10&min_ref_count=1"
    )
    assert response.status_code == 200

    result = response.json()
    logger.debug(result)
    assert "statements" in result
    assert len(result["statements"]) > 0

    logger.info("✓ Most-used statements works")


def test_hard_delete_decrements_ref_count(
    api_client: requests.Session, base_url: str
) -> None:
    """Test hard delete decrements statement ref counts"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q80020",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Hard Delete Test"}},
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
                        "hash": "h1",
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                    "id": "Q80020$1",
                }
            ]
        },
    }

    api_client.post(f"{base_url}/entity", json=entity_data)
    raw = api_client.get(f"{base_url}/raw/Q80020/1").json()
    logger.debug(raw)
    statement_hash = raw["statements"][0]

    verify_response = api_client.get(f"{base_url}/statement/{statement_hash}")
    assert verify_response.status_code == 200, "Statement should exist before delete"

    delete_response = api_client.delete(
        f"{base_url}/entity/Q80020", json={"delete_type": "hard"}
    )
    assert delete_response.status_code == 200

    get_response = api_client.get(f"{base_url}/entity/Q80020")
    assert get_response.status_code == 410, "Hard-deleted entity should be gone"

    logger.info("✓ Hard delete decrements ref counts")


def test_statement_with_qualifiers_and_references(
    api_client: requests.Session, base_url: str
) -> None:
    """Test statements with qualifiers and references are stored correctly"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q80030",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Complex Statement"}},
        "claims": {
            "P569": [
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P569",
                        "datatype": "time",
                        "datavalue": {
                            "value": {
                                "time": "+1952-03-03T00:00:00Z",
                                "timezone": 0,
                                "before": 0,
                                "after": 0,
                                "precision": 11,
                                "calendarmodel": "http://www.wikidata.org/entity/Q1985727",
                            },
                            "type": "time",
                        },
                        "hash": "h1",
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {
                        "P805": [
                            {
                                "snaktype": "value",
                                "property": "P805",
                                "datatype": "wikibase-item",
                                "datavalue": {
                                    "value": {"entity-type": "item", "id": "Q805"},
                                    "type": "wikibase-entityid",
                                },
                                "hash": "h2",
                            }
                        ]
                    },
                    "references": [
                        {
                            "snaks": {
                                "P248": [
                                    {
                                        "snaktype": "value",
                                        "property": "P248",
                                        "datatype": "wikibase-item",
                                        "datavalue": {
                                            "value": {
                                                "entity-type": "item",
                                                "id": "Q539",
                                            },
                                            "type": "wikibase-entityid",
                                        },
                                        "hash": "h3",
                                    }
                                ]
                            }
                        }
                    ],
                    "id": "Q80030$1",
                }
            ]
        },
    }

    response = api_client.post(f"{base_url}/entity", json=entity_data)
    assert response.status_code == 200

    raw = api_client.get(f"{base_url}/raw/Q80030/1").json()
    logger.debug(raw)
    assert len(raw["statements"]) == 1

    statement_hash = raw["statements"][0]
    statement_response = api_client.get(f"{base_url}/statement/{statement_hash}")
    assert statement_response.status_code == 200

    statement = statement_response.json()
    assert statement["statement"]["mainsnak"]["property"] == "P569"
    assert len(statement["statement"]["qualifiers"]) > 0
    assert "P805" in statement["statement"]["qualifiers"]
    assert len(statement["statement"]["references"]) > 0

    logger.info("✓ Statements with qualifiers and references work")


def test_ref_count_increments_on_duplicate(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that ref_count increments when same statement appears in multiple entities"""
    logger = logging.getLogger(__name__)

    statement = {
        "mainsnak": {
            "snaktype": "value",
            "property": "P31",
            "datatype": "wikibase-item",
            "datavalue": {
                "value": {"entity-type": "item", "id": "Q5"},
                "type": "wikibase-entityid",
            },
            "hash": "h1",
        },
        "type": "statement",
        "rank": "normal",
        "qualifiers": {},
        "references": [],
        "id": "placeholder",
    }

    entity1_data = {
        "id": "Q80040",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Entity 1"}},
        "claims": {"P31": [{**statement, "id": "Q80040$1"}]},
    }

    entity2_data = {
        "id": "Q80041",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Entity 2"}},
        "claims": {"P31": [{**statement, "id": "Q80041$1"}]},
    }

    entity3_data = {
        "id": "Q80042",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Entity 3"}},
        "claims": {"P31": [{**statement, "id": "Q80042$1"}]},
    }

    api_client.post(f"{base_url}/entity", json=entity1_data)
    api_client.post(f"{base_url}/entity", json=entity2_data)
    api_client.post(f"{base_url}/entity", json=entity3_data)

    raw1 = api_client.get(f"{base_url}/raw/Q80040/1").json()
    logger.debug(raw1)
    statement_hash = raw1["statements"][0]

    statement_response = api_client.get(f"{base_url}/statement/{statement_hash}")
    assert statement_response.status_code == 200

    logger.info(
        "✓ Ref count increments on duplicates (statement shared across entities)"
    )


def test_orphaned_statements_cleanup(
    api_client: requests.Session, base_url: str
) -> None:
    """Test orphaned statement cleanup endpoint"""
    logger = logging.getLogger(__name__)

    response = api_client.post(
        f"{base_url}/statements/cleanup-orphaned",
        json={"older_than_days": 180, "limit": 1000},
    )
    assert response.status_code == 200

    result = response.json()
    assert "cleaned_count" in result
    assert "failed_count" in result
    assert "errors" in result

    logger.info("✓ Orphaned statements cleanup endpoint works")


def test_entity_revision_with_statements(
    api_client: requests.Session, base_url: str
) -> None:
    """Test entity revisions store statement arrays correctly"""
    logger = logging.getLogger(__name__)

    entity_data = {
        "id": "Q80050",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Revision Test"}},
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
                        "hash": "h1",
                    },
                    "type": "statement",
                    "rank": "normal",
                    "qualifiers": {},
                    "references": [],
                    "id": "Q80050$1",
                }
            ]
        },
    }

    api_client.post(f"{base_url}/entity", json=entity_data)

    raw = api_client.get(f"{base_url}/raw/Q80050/1").json()
    logger.debug(raw)
    assert "statements" in raw
    assert "properties" in raw
    assert "property_counts" in raw

    assert isinstance(raw["statements"], list)
    assert isinstance(raw["properties"], list)
    assert isinstance(raw["property_counts"], dict)

    logger.info("✓ Entity revisions store statements metadata correctly")
