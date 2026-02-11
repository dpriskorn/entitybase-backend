"""Unit tests for Entity internal representation."""

from models.data.infrastructure.s3.enums import EntityType
from models.data.rest_api.v1.entitybase.response import (
    EntityLabelsResponse,
    EntityDescriptionsResponse,
    EntityAliasesResponse,
)
from models.internal_representation.entity import Entity


class TestEntity:
    """Unit tests for Entity model."""

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
