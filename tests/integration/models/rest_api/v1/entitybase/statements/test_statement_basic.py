import requests


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
