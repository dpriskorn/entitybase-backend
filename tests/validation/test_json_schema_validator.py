import sys

sys.path.insert(0, "src")

import pytest
from jsonschema import ValidationError

from models.validation.json_schema_validator import JsonSchemaValidator


@pytest.fixture
def validator() -> JsonSchemaValidator:
    return JsonSchemaValidator()


def test_valid_entity_revision(validator: JsonSchemaValidator) -> None:
    valid_entity = {
        "schema_version": "1.2.0",
        "revision_id": 1,
        "created_at": "2026-01-07T10:00:00Z",
        "created_by": "test-user",
        "entity_type": "item",
        "entity": {
            "id": "Q42",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Douglas Adams"}},
            "descriptions": {"en": {"language": "en", "value": "English author"}},
            "aliases": {"en": [{"language": "en", "value": "DA"}]},
            "sitelinks": {"enwiki": {"site": "enwiki", "title": "Douglas Adams"}},
        },
        "statements": [123456789, 987654321],
        "properties": ["P31", "P569"],
        "property_counts": {"P31": 1, "P569": 1},
    }
    validator.validate_entity_revision(valid_entity)


def test_valid_entity_minimal(validator: JsonSchemaValidator) -> None:
    minimal_entity = {
        "schema_version": "1.2.0",
        "revision_id": 1,
        "created_at": "2026-01-07T10:00:00Z",
        "created_by": "test-user",
        "entity_type": "item",
        "entity": {
            "id": "Q42",
            "type": "item",
        },
        "statements": [],
        "properties": [],
        "property_counts": {},
    }
    validator.validate_entity_revision(minimal_entity)


def test_invalid_entity_missing_required_field(validator: JsonSchemaValidator) -> None:
    invalid_entity = {
        "schema_version": "1.2.0",
        "revision_id": 1,
        "created_at": "2026-01-07T10:00:00Z",
        "created_by": "test-user",
        "entity_type": "item",
        "entity": {
            "id": "Q42",
        },
        "statements": [],
        "properties": [],
        "property_counts": {},
    }
    with pytest.raises(ValidationError):
        validator.validate_entity_revision(invalid_entity)


def test_invalid_entity_wrong_type(validator: JsonSchemaValidator) -> None:
    invalid_entity = {
        "schema_version": "1.2.0",
        "revision_id": "not-a-number",
        "created_at": "2026-01-07T10:00:00Z",
        "created_by": "test-user",
        "entity_type": "item",
        "entity": {
            "id": "Q42",
            "type": "item",
        },
        "statements": [],
        "properties": [],
        "property_counts": {},
    }
    with pytest.raises(ValidationError):
        validator.validate_entity_revision(invalid_entity)


def test_invalid_entity_id_format(validator: JsonSchemaValidator) -> None:
    invalid_entity = {
        "schema_version": "1.2.0",
        "revision_id": 1,
        "created_at": "2026-01-07T10:00:00Z",
        "created_by": "test-user",
        "entity_type": "item",
        "entity": {
            "id": "not-valid",
            "type": "item",
        },
        "statements": [],
        "properties": [],
        "property_counts": {},
    }
    with pytest.raises(ValidationError):
        validator.validate_entity_revision(invalid_entity)


def test_invalid_entity_type_enum(validator: JsonSchemaValidator) -> None:
    invalid_entity = {
        "schema_version": "1.2.0",
        "revision_id": 1,
        "created_at": "2026-01-07T10:00:00Z",
        "created_by": "test-user",
        "entity_type": "invalid-type",
        "entity": {
            "id": "Q42",
            "type": "item",
        },
        "statements": [],
        "properties": [],
        "property_counts": {},
    }
    with pytest.raises(ValidationError):
        validator.validate_entity_revision(invalid_entity)


def test_valid_statement(validator: JsonSchemaValidator) -> None:
    valid_statement = {
        "content_hash": 123456789,
        "statement": {
            "mainsnak": {
                "snaktype": "value",
                "property": "P31",
                "datatype": "wikibase-item",
                "hash": "123abc",
            },
            "type": "statement",
            "rank": "normal",
            "qualifiers": {},
            "references": [],
        },
        "created_at": "2026-01-07T10:00:00Z",
    }
    validator.validate_statement(valid_statement)


def test_invalid_statement_missing_required_field(
    validator: JsonSchemaValidator,
) -> None:
    invalid_statement = {
        "content_hash": 123456789,
        "statement": {
            "property": "P31",
            "datatype": "wikibase-item",
        },
        "created_at": "2026-01-07T10:00:00Z",
    }
    with pytest.raises(ValidationError):
        validator.validate_statement(invalid_statement)


def test_invalid_statement_wrong_enum(validator: JsonSchemaValidator) -> None:
    invalid_statement = {
        "content_hash": 123456789,
        "statement": {
            "mainsnak": {
                "snaktype": "invalid-snack",
                "property": "P31",
                "datatype": "wikibase-item",
                "hash": "123abc",
            },
            "rank": "invalid-rank",
        },
        "created_at": "2026-01-07T10:00:00Z",
    }
    with pytest.raises(ValidationError):
        validator.validate_statement(invalid_statement)
