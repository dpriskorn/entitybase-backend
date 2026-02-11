"""Internal representation of Wikibase entities."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from models.data.infrastructure.s3.enums import EntityType
from models.internal_representation.statements import Statement
from models.data.rest_api.v1.entitybase.response import (
    EntityLabelsResponse,
    EntityDescriptionsResponse,
    EntityAliasesResponse,
)
from models.data.rest_api.v1.entitybase.response import EntitySitelinksResponse


class Entity(BaseModel):
    """Internal representation of a Wikibase entity."""

    id: str
    type: EntityType
    labels: EntityLabelsResponse
    descriptions: EntityDescriptionsResponse
    aliases: EntityAliasesResponse
    statements: list[Statement]
    sitelinks: Optional[EntitySitelinksResponse] = Field(default=None)

    model_config = ConfigDict(frozen=True)

    def get_entity_type(self) -> str:
        """Get the entity type as string."""
        return self.type.value
