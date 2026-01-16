"""Tests for entity response models."""

import pytest
from pydantic import ValidationError

from models.rest_api.entitybase.response.entity import (
    AliasValue,
    DescriptionValue,
    EntityAliases,
    EntityDescriptions,
    EntityLabels,
    EntityMetadata,
    EntitySitelinks,
    EntityStatements,
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
        labels = EntityLabels(data=data)
        assert len(labels.data) == 2
        assert labels.data["en"].value == "English label"

    def test_entity_labels_invalid_structure(self):
        """Test EntityLabels with invalid nested structure."""
        data = {
            "en": {"invalid": "structure"}  # Missing language/value
        }
        with pytest.raises(ValidationError):
            EntityLabels(data=data)

    def test_entity_descriptions_valid(self):
        """Test EntityDescriptions with valid data."""
        data = {"en": {"language": "en", "value": "English description"}}
        descriptions = EntityDescriptions(data=data)
        assert descriptions.data["en"].value == "English description"

    def test_entity_aliases_valid(self):
        """Test EntityAliases with valid data."""
        data = {
            "en": [
                {"language": "en", "value": "alias1"},
                {"language": "en", "value": "alias2"},
            ]
        }
        aliases = EntityAliases(data=data)
        assert len(aliases.data["en"]) == 2

    def test_entity_statements_valid(self):
        """Test EntityStatements with valid data."""
        data = [{"property": "P31", "value": "Q5"}]
        statements = EntityStatements(data=data)
        assert len(statements.data) == 1

    def test_entity_sitelinks_valid(self):
        """Test EntitySitelinks with valid data."""
        data = {"enwiki": {"title": "Test Page"}}
        sitelinks = EntitySitelinks(data=data)
        assert sitelinks.data["enwiki"]["title"] == "Test Page"


class TestEntityMetadata:
    """Test EntityMetadata model."""

    def test_entity_metadata_minimal(self):
        """Test minimal EntityMetadata creation."""
        metadata = EntityMetadata(id="Q123")
        assert metadata.id == "Q123"
        assert metadata.type == "item"
        assert metadata.labels.data == {}
        assert metadata.descriptions.data == {}
        assert metadata.aliases.data == {}
        assert metadata.statements.data == []
        assert metadata.sitelinks.data == {}

    def test_entity_metadata_full(self):
        """Test EntityMetadata with full data."""
        metadata = EntityMetadata(
            id="Q123",
            type="property",
            labels=EntityLabels(data={"en": {"language": "en", "value": "Test Label"}}),
            descriptions=EntityDescriptions(
                data={"en": {"language": "en", "value": "Test Description"}}
            ),
            aliases=EntityAliases(
                data={"en": [{"language": "en", "value": "Test Alias"}]}
            ),
            statements=EntityStatements(data=[{"property": "P31"}]),
            sitelinks=EntitySitelinks(data={"enwiki": {"title": "Test"}}),
        )
        assert metadata.id == "Q123"
        assert metadata.type == "property"
        assert metadata.labels.data["en"].value == "Test Label"

    def test_entity_metadata_invalid_id(self):
        """Test EntityMetadata with invalid data raises error."""
        with pytest.raises(ValidationError):
            EntityMetadata(labels=EntityLabels(data={"en": {"invalid": "structure"}}))
