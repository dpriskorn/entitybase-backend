from typing import Optional, Any

"""Internal representation of Wikibase entities."""

from pydantic import BaseModel, ConfigDict, Field

from models.rest_api.response.entity.wikibase import (
    EntityAliases,
    EntityDescriptions,
    EntityLabels,
)
from models.internal_representation.entity_types import EntityKind
from models.internal_representation.statements import Statement


class Entity(BaseModel):
    """Internal representation of a Wikibase entity."""

    id: str
    type: EntityKind
    labels: EntityLabels
    descriptions: EntityDescriptions
    aliases: EntityAliases
    statements: list[Statement]
    sitelinks: Optional[dict[str, dict[str, Any]]] = Field(default=None)

    model_config = ConfigDict(frozen=True)
