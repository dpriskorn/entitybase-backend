import logging
import requests


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


def test_statement_deduplication(api_client: requests.Session, base_url: str) -> None:
    """Test that identical statements are deduplicated and reference count incremented"""
    logger = logging.getLogger(__name__)

    # Create first entity with statement
    entity1_data = {
        "id": "Q80002",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Deduplication 1"}},
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

    response1 = api_client.post(f"{base_url}/entity", json=entity1_data)
    assert response1.status_code == 200

    # Create second entity with identical statement
    entity2_data = {
        "id": "Q80003",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Deduplication 2"}},
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

    response2 = api_client.post(f"{base_url}/entity", json=entity2_data)
    assert response2.status_code == 200

    # Check that both entities have the same statement hash
    raw1 = api_client.get(f"{base_url}/raw/Q80002/1").json()
    raw2 = api_client.get(f"{base_url}/raw/Q80003/1").json()

    assert len(raw1["statements"]) == 1
    assert len(raw2["statements"]) == 1
    assert raw1["statements"][0] == raw2["statements"][0], "Statements should be deduplicated"

    statement_hash = raw1["statements"][0]

    # Check reference count
    ref_response = api_client.get(f"{base_url}/statement/{statement_hash}/refs")
    assert ref_response.status_code == 200
    ref_data = ref_response.json()
    assert ref_data["count"] == 2, "Reference count should be 2"


def test_get_single_statement(api_client: requests.Session, base_url: str) -> None:
    """Test fetching a single statement by hash"""
    # Create entity with statement first
    entity_data = {
        "id": "Q80004",
        "type": "item",
        "labels": {"en": {"language": "en", "value": "Test Single Statement"}},
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

    response = api_client.post(f"{base_url}/entity", json=entity_data)
    assert response.status_code == 200

    # Get the statement hash
    raw = api_client.get(f"{base_url}/raw/Q80004/1").json()
    statement_hash = raw["statements"][0]

    # Fetch the statement
    stmt_response = api_client.get(f"{base_url}/statement/{statement_hash}")
    assert stmt_response.status_code == 200
    statement = stmt_response.json()

    # Verify structure
    assert "statement" in statement
    assert "entity_id" in statement
    assert "revision_id" in statement
    assert statement["entity_id"] == "Q80004"
    assert statement["revision_id"] == 1

    stmt_data = statement["statement"]
    assert stmt_data["property"] == "P31"
    assert stmt_data["mainsnak"]["datavalue"]["value"]["id"] == "Q5"


def test_get_nonexistent_statement_404(
    api_client: requests.Session, base_url: str
) -> None:
    """Test fetching nonexistent statement returns 404"""
    response = api_client.get(f"{base_url}/statement/999999")
    assert response.status_code == 404


def test_entity_revision_with_statements(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that entity revisions include statement hashes"""
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

    response = api_client.post(f"{base_url}/entity", json=entity_data)
    assert response.status_code == 200

    # Get entity
    entity_response = api_client.get(f"{base_url}/entity/Q80005")
    assert entity_response.status_code == 200
    entity = entity_response.json()

    assert "statements" in entity
    assert len(entity["statements"]) == 1
    assert isinstance(entity["statements"][0], int)


def test_invalid_statement_rejected(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that invalid statements are rejected"""
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

    response = api_client.post(f"{base_url}/entity", json=entity_data)
    assert response.status_code == 400