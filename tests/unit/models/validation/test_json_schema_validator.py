import sys

sys.path.insert(0, "src")

import pytest

pytestmark = pytest.mark.unit

from models.validation.json_schema_validator import JsonSchemaValidator


@pytest.fixture
def validator() -> JsonSchemaValidator:
    return JsonSchemaValidator()


# TODO: Reimplement test_valid_entity_revision with S3RevisionData validation
# Removed temporarily due to RevisionData vs entity schema validation mismatch
# Will be reimplemented once S3RevisionData separation is complete


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
            "schema_version": "1.0.0",
            "id": "Q42",
        },
        "statements": [],
        "properties": [],
        "property_counts": {},
    }
    with pytest.raises(ValueError):
        validator.validate_entity_revision(invalid_entity)


def test_invalid_entity_wrong_type(validator: JsonSchemaValidator) -> None:
    invalid_entity = {
        "schema_version": "1.2.0",
        "revision_id": "not-a-number",
        "created_at": "2026-01-07T10:00:00Z",
        "created_by": "test-user",
        "entity_type": "item",
        "entity": {
            "schema_version": "1.0.0",
            "id": "Q42",
            "type": "item",
        },
        "statements": [],
        "properties": [],
        "property_counts": {},
    }
    with pytest.raises(ValueError):
        validator.validate_entity_revision(invalid_entity)


def test_invalid_entity_id_format(validator: JsonSchemaValidator) -> None:
    invalid_entity = {
        "schema_version": "1.2.0",
        "revision_id": 1,
        "created_at": "2026-01-07T10:00:00Z",
        "created_by": "test-user",
        "entity_type": "item",
        "entity": {
            "schema_version": "1.0.0",
            "id": "not-valid",
            "type": "item",
        },
        "statements": [],
        "properties": [],
        "property_counts": {},
    }
    with pytest.raises(ValueError):
        validator.validate_entity_revision(invalid_entity)


def test_invalid_entity_type_enum(validator: JsonSchemaValidator) -> None:
    invalid_entity = {
        "schema_version": "1.2.0",
        "revision_id": 1,
        "created_at": "2026-01-07T10:00:00Z",
        "created_by": "test-user",
        "entity_type": "invalid-type",
        "entity": {
            "schema_version": "1.0.0",
            "id": "Q42",
            "type": "item",
        },
        "statements": [],
        "properties": [],
        "property_counts": {},
    }
    with pytest.raises(ValueError):
        validator.validate_entity_revision(invalid_entity)


def test_valid_statement(validator: JsonSchemaValidator) -> None:
    valid_statement = {
        "schema_version": "1.0.0",
        "content_hash": 123456789,
        "statement": {
            "mainsnak": 12345,
            "type": "statement",
            "rank": "normal",
            "qualifiers": [12345],
            "references": [12345],
        },
        "created_at": "2026-01-07T10:00:00Z",
    }
    validator.validate_statement(valid_statement)


def test_invalid_statement_missing_required_field(
    validator: JsonSchemaValidator,
) -> None:
    invalid_statement = {
        "schema_version": "1.0.0",
        "content_hash": 123456789,
        "statement": {
            "property": "P31",
            "datatype": "wikibase-item",
        },
        "created_at": "2026-01-07T10:00:00Z",
    }
    with pytest.raises(ValueError):
        validator.validate_statement(invalid_statement)


def test_invalid_statement_wrong_enum(validator: JsonSchemaValidator) -> None:
    invalid_statement = {
        "schema_version": "1.0.0",
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
    with pytest.raises(ValueError):
        validator.validate_statement(invalid_statement)


def test_valid_statement_with_hashes(validator: JsonSchemaValidator) -> None:
    valid_statement = {
        "schema_version": "1.0.0",
        "content_hash": 123456789,
        "statement": {
            "mainsnak": 12345,
            "type": "statement",
            "rank": "normal",
            "qualifiers": [12345],
            "references": [12345],
        },
        "created_at": "2026-01-07T10:00:00Z",
    }
    validator.validate_statement(valid_statement)
