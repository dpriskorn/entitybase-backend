import json
import jsonschema
import pytest
import requests
from pathlib import Path


def test_wikibase_schema_validation_unit() -> None:
    """Unit test for Wikibase entity schema validation."""
    # Sample Wikibase entity data
    sample_entity = {
        "id": "Q42",
        "type": "item",
        "labels": {
            "en": {"language": "en", "value": "Douglas Adams"},
            "de": {"language": "de", "value": "Douglas Adams"},
        },
        "descriptions": {
            "en": {"language": "en", "value": "English writer and humorist"}
        },
        "aliases": {"en": [{"language": "en", "value": "Douglas Noel Adams"}]},
        "claims": {
            "P31": [  # instance of
                {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P31",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q5"},
                            "type": "wikibase-entityid",
                        },
                    },
                    "type": "statement",
                    "rank": "normal",
                }
            ]
        },
        "sitelinks": {
            "enwiki": {"site": "enwiki", "title": "Douglas Adams", "badges": []}
        },
    }

    # Load the schema
    schema_path = (
        Path(__file__).parent.parent.parent
        / "src"
        / "schemas"
        / "wikibase"
        / "entity"
        / "latest"
        / "latest.json"
    )
    with open(schema_path, "r") as f:
        schema = json.load(f)

    # Validate - should pass
    jsonschema.validate(sample_entity, schema)

    # Test invalid entity - should fail
    invalid_entity = sample_entity.copy()
    invalid_entity["type"] = "invalid_type"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(invalid_entity, schema)


def test_wikibase_item_endpoint_validates_schema(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that the wikibase item endpoint returns valid Wikibase entity JSON."""
    # Get entity Q1 (assuming it exists in test data)
    response = api_client.get(f"{base_url}/wikibase/v1/entities/items/Q1")
    assert response.status_code == 200

    entity_data = response.json()

    # Load the schema
    schema_path = (
        Path(__file__).parent.parent.parent
        / "src"
        / "schemas"
        / "wikibase"
        / "entity"
        / "latest"
        / "latest.json"
    )
    with open(schema_path, "r") as f:
        schema = json.load(f)

    # Validate against schema
    jsonschema.validate(entity_data, schema)


def test_wikibase_property_endpoint_validates_schema(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that the wikibase property endpoint returns valid Wikibase entity JSON."""
    # Get property P31 (assuming it exists)
    response = api_client.get(f"{base_url}/wikibase/v1/entities/properties/P31")
    assert response.status_code == 200

    entity_data = response.json()

    # Load the schema
    schema_path = (
        Path(__file__).parent.parent.parent
        / "src"
        / "schemas"
        / "wikibase"
        / "entity"
        / "latest"
        / "latest.json"
    )
    with open(schema_path, "r") as f:
        schema = json.load(f)

    # Validate against schema
    jsonschema.validate(entity_data, schema)


def test_wikibase_lexeme_endpoint_validates_schema(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that the wikibase lexeme endpoint returns valid Wikibase entity JSON."""
    # Assuming a lexeme exists, e.g., L1
    response = api_client.get(f"{base_url}/wikibase/v1/entities/lexemes/L1")
    if response.status_code == 404:
        pytest.skip("Lexeme L1 not found in test data")
    assert response.status_code == 200

    entity_data = response.json()

    # Load the schema
    schema_path = (
        Path(__file__).parent.parent.parent
        / "src"
        / "schemas"
        / "wikibase"
        / "entity"
        / "latest"
        / "latest.json"
    )
    with open(schema_path, "r") as f:
        schema = json.load(f)

    # Validate against schema
    jsonschema.validate(entity_data, schema)


def test_wikibase_item_create_redirects(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that POST to wikibase item create redirects to entitybase."""
    data = {"type": "item", "labels": {"en": {"language": "en", "value": "Test Item"}}}
    response = api_client.post(f"{base_url}/wikibase/v1/entities/items", json=data)
    assert response.status_code == 307
    assert response.headers.get("location") == "/entitybase/v1/entities/items"


def test_wikibase_property_create_redirects(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that POST to wikibase property create redirects to entitybase."""
    data = {
        "type": "property",
        "labels": {"en": {"language": "en", "value": "Test Property"}},
    }
    response = api_client.post(f"{base_url}/wikibase/v1/entities/properties", json=data)
    assert response.status_code == 307
    assert response.headers.get("location") == "/entitybase/v1/entities/properties"


def test_wikibase_lexeme_create_redirects(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that POST to wikibase lexeme create redirects to entitybase."""
    data = {
        "type": "lexeme",
        "labels": {"en": {"language": "en", "value": "Test Lexeme"}},
    }
    response = api_client.post(f"{base_url}/wikibase/v1/entities/lexemes", json=data)
    assert response.status_code == 307
    assert response.headers.get("location") == "/entitybase/v1/entities/lexemes"


def test_wikibase_item_update_redirects(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that PUT to wikibase item update redirects to entitybase."""
    data = {"labels": {"en": {"language": "en", "value": "Updated Test Item"}}}
    response = api_client.put(f"{base_url}/wikibase/v1/entities/items/Q1", json=data)
    assert response.status_code == 307
    assert response.headers.get("location") == "/entitybase/v1/item/Q1"


def test_wikibase_property_update_redirects(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that PUT to wikibase property update redirects to entitybase."""
    data = {"labels": {"en": {"language": "en", "value": "Updated Test Property"}}}
    response = api_client.put(
        f"{base_url}/wikibase/v1/entities/properties/P31", json=data
    )
    assert response.status_code == 307
    assert response.headers.get("location") == "/entitybase/v1/property/P31"


def test_wikibase_lexeme_update_redirects(
    api_client: requests.Session, base_url: str
) -> None:
    """Test that PUT to wikibase lexeme update redirects to entitybase."""
    data = {"labels": {"en": {"language": "en", "value": "Updated Test Lexeme"}}}
    response = api_client.put(f"{base_url}/wikibase/v1/entities/lexemes/L1", json=data)
    assert response.status_code == 307
    assert response.headers.get("location") == "/entitybase/v1/lexeme/L1"
