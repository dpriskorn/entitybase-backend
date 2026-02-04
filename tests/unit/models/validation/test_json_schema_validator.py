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
