"""Internal representation of Wikibase entities."""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from models.data.infrastructure.s3.enums import EntityType
from models.internal_representation.statements import Statement
from models.rest_api.entitybase.v1.response import (
    EntityLabelsResponse,
    EntityDescriptionsResponse,
    EntityAliasesResponse,
)
from models.rest_api.entitybase.v1.response.entity import EntitySitelinksResponse


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

