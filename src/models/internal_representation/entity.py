"""Internal representation of Wikibase entities."""

from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from models.infrastructure.s3.enums import EntityType
from models.internal_representation.statements import Statement

if TYPE_CHECKING:
    from models.rest_api.entitybase.response import (
        EntityLabelsResponse,
        EntityDescriptionsResponse,
        EntityAliasesResponse,
    )
    from models.rest_api.entitybase.response.entity import EntitySitelinksResponse


class Entity(BaseModel):
    """Internal representation of a Wikibase entity."""

    id: str
    type: EntityType
    labels: "EntityLabelsResponse"
    descriptions: "EntityDescriptionsResponse"
    aliases: "EntityAliasesResponse"
    statements: list[Statement]
    sitelinks: Optional["EntitySitelinksResponse"] = Field(default=None)

    model_config = ConfigDict(frozen=True)


# Import referenced classes and rebuild model to resolve forward references
from models.rest_api.entitybase.response.entity.entitybase import (
    EntityLabelsResponse,
    EntityDescriptionsResponse,
    EntityAliasesResponse,
    EntitySitelinksResponse,
)

Entity.model_rebuild()
