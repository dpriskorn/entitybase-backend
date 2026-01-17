"""Tests for entity response models."""

import pytest

pytestmark = pytest.mark.unit
from pydantic import ValidationError

from models.rest_api.entitybase.response.entity import (
    AliasValue,
    DescriptionValue,
    EntityAliasesResponse,
    EntityChange,
    EntityDescriptionsResponse,
    EntityLabelsResponse,
    EntityMetadataResponse,
    EntitySitelinksResponse,

# Rebuild model after imports
EntityChange.model_rebuild()
    EntityStatementsResponse,
    LabelValue,
)


class TestValueModels:
    """Test individual value models."""

    def test_label_value_valid(self):
        """Test valid LabelValue creation."""
        label = LabelValue(language="en", value="Test Label")
        assert label.language == "en"
        assert label.value == "Test Label"

    def test_label_value_empty_language(self):
        """Test LabelValue with empty language raises error."""
        with pytest.raises(ValidationError):
            LabelValue(language="", value="Test")

    def test_label_value_empty_value(self):
        """Test LabelValue with empty value raises error."""
        with pytest.raises(ValidationError):
            LabelValue(language="en", value="")

    def test_description_value_valid(self):
        """Test valid DescriptionValue creation."""
        desc = DescriptionValue(language="en", value="Test description")
        assert desc.language == "en"
        assert desc.value == "Test description"

    def test_alias_value_valid(self):
        """Test valid AliasValue creation."""
        alias = AliasValue(language="en", value="Test alias")
        assert alias.language == "en"
        assert alias.value == "Test alias"


class TestCollectionModels:
    """Test collection models."""

    def test_entity_labels_valid(self):
        """Test EntityLabels with valid data."""
        data = {
            "en": {"language": "en", "value": "English label"},
            "de": {"language": "de", "value": "German label"},
        }
        labels = EntityLabelsResponse(data=data)
        assert len(labels.data) == 2
        assert labels.data["en"].value == "English label"

    def test_entity_labels_invalid_structure(self):
        """Test EntityLabels with invalid nested structure."""
        data = {
            "en": {"invalid": "structure"}  # Missing language/value
        }
        with pytest.raises(ValidationError):
            EntityLabelsResponse(data=data)

    def test_entity_descriptions_valid(self):
        """Test EntityDescriptions with valid data."""
        data = {"en": {"language": "en", "value": "English description"}}
        descriptions = EntityDescriptionsResponse(data=data)
        assert descriptions.data["en"].value == "English description"

    def test_entity_aliases_valid(self):
        """Test EntityAliases with valid data."""
        data = {
            "en": [
                {"language": "en", "value": "alias1"},
                {"language": "en", "value": "alias2"},
            ]
        }
        aliases = EntityAliasesResponse(data=data)
        assert len(aliases.data["en"]) == 2

    def test_entity_statements_valid(self):
        """Test EntityStatements with valid data."""
        data = [{"property": "P31", "value": "Q5"}]
        statements = EntityStatementsResponse(data=data)
        assert len(statements.data) == 1

    def test_entity_sitelinks_valid(self):
        """Test EntitySitelinks with valid data."""
        data = {
            "enwiki": {"site": "enwiki", "title": "Test Page", "url": "", "badges": []}
        }
        sitelinks = EntitySitelinksResponse(data=data)
        assert sitelinks.data["enwiki"].title == "Test Page"


class TestEntityMetadata:
    """Test EntityMetadata model."""

    def test_entity_metadata_minimal(self):
        """Test minimal EntityMetadata creation."""
        metadata = EntityMetadataResponse(id="Q123")
        assert metadata.id == "Q123"
        assert metadata.type == "item"
        assert metadata.labels.data == {}
        assert metadata.descriptions.data == {}
        assert metadata.aliases.data == {}
        assert metadata.statements.data == []
        assert metadata.sitelinks.data == {}

    def test_entity_metadata_full(self):
        """Test EntityMetadata with full data."""
        metadata = EntityMetadataResponse(
            id="Q123",
            type="property",
            labels=EntityLabelsResponse(
                data={"en": {"language": "en", "value": "Test Label"}}
            ),
            descriptions=EntityDescriptionsResponse(
                data={"en": {"language": "en", "value": "Test Description"}}
            ),
            aliases=EntityAliasesResponse(
                data={"en": [{"language": "en", "value": "Test Alias"}]}
            ),
            statements=EntityStatementsResponse(data=[{"property": "P31"}]),
            sitelinks=EntitySitelinksResponse(
                data={
                    "enwiki": {
                        "site": "enwiki",
                        "title": "Test",
                        "url": "",
                        "badges": [],
                    }
                }
            ),
        )
        assert metadata.id == "Q123"
        assert metadata.type == "property"
        assert metadata.labels.data["en"].value == "Test Label"

    def test_entity_metadata_invalid_id(self):
        """Test EntityMetadata with invalid data raises error."""
        with pytest.raises(ValidationError):
            EntityMetadataResponse(
                labels=EntityLabelsResponse(data={"en": {"invalid": "structure"}})
            )


class TestEntityChange:
    """Test EntityChange model."""

    def test_entity_change_valid(self):
        """Test valid EntityChange creation."""
        from datetime import datetime
        from models.infrastructure.stream.change_type import ChangeType

        change = EntityChange(
            entity_id="Q42",
            revision_id=123,
            change_type=ChangeType.EDIT,
            from_revision_id=122,
            changed_at=datetime(2023, 1, 1, 12, 0, 0),
            edit_summary="Updated label",
            bot=False,
        )
        assert change.entity_id == "Q42"
        assert change.revision_id == 123
        assert change.change_type == ChangeType.EDIT
        assert change.from_revision_id == 122
        assert change.edit_summary == "Updated label"

    def test_entity_change_minimal(self):
        """Test EntityChange with minimal required fields."""
        from datetime import datetime
        from models.infrastructure.stream.change_type import ChangeType

        change = EntityChange(
            entity_id="Q42",
            revision_id=123,
            change_type=ChangeType.CREATION,
            changed_at=datetime(2023, 1, 1, 12, 0, 0),
        )
        assert change.entity_id == "Q42"
        assert change.revision_id == 123
        assert change.change_type == ChangeType.CREATION
        assert change.from_revision_id == 0  # default
        assert change.edit_summary == ""  # default

    def test_entity_change_invalid_change_type(self):
        """Test EntityChange with invalid change_type raises error."""
        from datetime import datetime

        with pytest.raises(ValidationError):
            EntityChange(
                entity_id="Q42",
                revision_id=123,
                change_type="invalid",  # not a ChangeType
                changed_at=datetime(2023, 1, 1, 12, 0, 0),
            )

    def test_entity_change_json_schema_validation(self):
        """Test EntityChange validates against JSON schema."""
        import json
        import jsonschema
        from datetime import datetime
        from models.infrastructure.stream.change_type import ChangeType

        # Load the schema
        with open("src/schemas/entitychange.json", "r") as f:
            schema = json.load(f)

        # Create a valid EntityChange
        change = EntityChange(
            entity_id="Q42",
            revision_id=123,
            change_type=ChangeType.EDIT,
            from_revision_id=122,
            changed_at=datetime(2023, 1, 1, 12, 0, 0),
            edit_summary="Updated label",
            bot=False,
        )

        # Convert to dict (model_dump)
        data = change.model_dump()

        # Validate against schema
        jsonschema.validate(instance=data, schema=schema)

        # Should not raise exception
        assert True
