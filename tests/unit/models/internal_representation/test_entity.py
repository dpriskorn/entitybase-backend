"""Unit tests for Entity internal representation."""

import pytest
from unittest.mock import MagicMock

from models.data.infrastructure.s3.enums import EntityType
from models.internal_representation.entity import Entity
from models.rest_api.entitybase.v1.response import (
    EntityLabelsResponse,
    EntityDescriptionsResponse,
    EntityAliasesResponse,
)
from models.rest_api.entitybase.v1.response.entity import EntitySitelinksResponse
from models.internal_representation.statements import Statement


class TestEntity:
    """Unit tests for Entity model."""

    def test_entity_creation_valid(self):
        """Test creating a valid Entity."""
        labels = EntityLabelsResponse(data={"en": {"language": "en", "value": "Test Entity"}})
        descriptions = EntityDescriptionsResponse(data={})
        aliases = EntityAliasesResponse(data={})
        statements = [MagicMock(spec=Statement)]
        sitelinks = EntitySitelinksResponse(sitelinks={})

        entity = Entity(
            id="Q123",
            type=EntityType.ITEM,
            labels=labels,
            descriptions=descriptions,
            aliases=aliases,
            statements=statements,
            sitelinks=sitelinks,
        )

        assert entity.id == "Q123"
        assert entity.type == EntityType.ITEM
        assert entity.labels.data == {"en": {"language": "en", "value": "Test Entity"}}
        assert entity.statements == statements
        assert entity.sitelinks == sitelinks

    def test_entity_creation_minimal(self):
        """Test creating Entity with minimal required fields."""
        labels = EntityLabelsResponse()
        descriptions = EntityDescriptionsResponse()
        aliases = EntityAliasesResponse()
        statements = []

        entity = Entity(
            id="Q456",
            type=EntityType.PROPERTY,
            labels=labels,
            descriptions=descriptions,
            aliases=aliases,
            statements=statements,
        )

        assert entity.id == "Q456"
        assert entity.type == EntityType.PROPERTY
        assert entity.sitelinks is None

    def test_entity_immutable(self):
        """Test that Entity is immutable (frozen)."""
        labels = EntityLabelsResponse()
        descriptions = EntityDescriptionsResponse()
        aliases = EntityAliasesResponse()
        statements = []

        entity = Entity(
            id="Q789",
            type=EntityType.ITEM,
            labels=labels,
            descriptions=descriptions,
            aliases=aliases,
            statements=statements,
        )

        with pytest.raises(TypeError, match="is immutable and does not support item assignment"):
            entity.id = "Q999"

    def test_entity_invalid_id(self):
        """Test Entity creation with invalid id."""
        labels = EntityLabelsResponse()
        descriptions = EntityDescriptionsResponse()
        aliases = EntityAliasesResponse()
        statements = []

        with pytest.raises(ValueError):  # Pydantic validation
            Entity(
                id="",  # Empty id
                type=EntityType.ITEM,
                labels=labels,
                descriptions=descriptions,
                aliases=aliases,
                statements=statements,
            )

    def test_entity_invalid_type(self):
        """Test Entity creation with invalid type."""
        labels = EntityLabelsResponse()
        descriptions = EntityDescriptionsResponse()
        aliases = EntityAliasesResponse()
        statements = []

        with pytest.raises(ValueError):  # Invalid enum value
            # noinspection PyTypeChecker
            Entity(
                id="Q123",
                type="invalid",  # Not an EntityType
                labels=labels,
                descriptions=descriptions,
                aliases=aliases,
                statements=statements,
            )

    def test_entity_get_entity_type(self):
        """Test get_entity_type method."""
        labels = EntityLabelsResponse()
        descriptions = EntityDescriptionsResponse()
        aliases = EntityAliasesResponse()
        statements = []

        entity = Entity(
            id="Q456",
            type=EntityType.PROPERTY,
            labels=labels,
            descriptions=descriptions,
            aliases=aliases,
            statements=statements,
        )

        result = entity.get_entity_type()

        assert result == "property"

    def test_entity_with_statements(self):
        """Test Entity with statements list."""
        labels = EntityLabelsResponse(data={"en": {"language": "en", "value": "Test"}})
        descriptions = EntityDescriptionsResponse(data={})
        aliases = EntityAliasesResponse(data={})
        statements = [MagicMock(), MagicMock()]

        entity = Entity(
            id="Q123",
            type=EntityType.ITEM,
            labels=labels,
            descriptions=descriptions,
            aliases=aliases,
            statements=statements,
        )

        assert len(entity.statements) == 2
        assert entity.id == "Q123"

    def test_entity_field_access(self):
        """Test accessing various fields."""
        labels = EntityLabelsResponse(data={"en": {"language": "en", "value": "Test"}})
        descriptions = EntityDescriptionsResponse(data={"en": {"language": "en", "value": "A test"}})
        aliases = EntityAliasesResponse(data={"en": [{"language": "en", "value": "Testing"}]})
        statements = []

        entity = Entity(
            id="Q789",
            type=EntityType.ITEM,
            labels=labels,
            descriptions=descriptions,
            aliases=aliases,
            statements=statements,
        )

        # Access fields to ensure coverage
        assert entity.labels.data["en"]["value"] == "Test"
        assert entity.descriptions.data["en"]["value"] == "A test"
        assert entity.aliases.data["en"][0]["value"] == "Testing"
        assert entity.statements == []
