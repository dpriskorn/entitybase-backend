"""Internal representation of Wikibase entities."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from models.internal_representation.entity_types import EntityKind
from models.internal_representation.statements import Statement
from models.rest_api.entitybase.response import (
    EntityLabelsResponse,
    EntityDescriptionsResponse,
    EntityAliasesResponse,
)
from models.rest_api.entitybase.response.entity import EntitySitelinksResponse


class Entity(BaseModel):
    """Internal representation of a Wikibase entity."""

    id: str
    type: EntityKind
    labels: EntityLabelsResponse
    descriptions: EntityDescriptionsResponse
    aliases: EntityAliasesResponse
    statements: list[Statement]
    sitelinks: Optional[EntitySitelinksResponse] = Field(default=None)

    model_config = ConfigDict(frozen=True)
