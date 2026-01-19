"""Internal representation of Wikibase entities."""

from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from models.infrastructure.s3.enums import EntityType
from models.internal_representation.statements import Statement
from models.rest_api.entitybase.v1.response import (
    EntityLabelsResponse,
    EntityDescriptionsResponse,
    EntityAliasesResponse,
)
from models.rest_api.entitybase.v1.response.entity import EntitySitelinksResponse

if TYPE_CHECKING:
    pass


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


# Import referenced classes and rebuild model to resolve forward references

# Entity.model_rebuild()
