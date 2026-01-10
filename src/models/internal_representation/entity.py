from typing import Optional, Any

from pydantic import BaseModel, ConfigDict

from models.api_models import EntityAliases, EntityDescriptions, EntityLabels
from models.internal_representation.entity_types import EntityKind
from models.internal_representation.statements import Statement


class Entity(BaseModel):
    id: str
    type: EntityKind
    labels: EntityLabels
    descriptions: EntityDescriptions
    aliases: EntityAliases
    statements: list[Statement]
    sitelinks: Optional[dict[str, dict[str, Any]]] = None

    model_config = ConfigDict(frozen=True)
