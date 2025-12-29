from typing import Optional, Any

from pydantic import BaseModel, ConfigDict

from models.internal_representation.entity_types import EntityKind
from models.internal_representation.statements import Statement


class Entity(BaseModel):
    id: str
    type: EntityKind
    labels: dict[str, str]
    descriptions: dict[str, str]
    aliases: dict[str, list[str]]
    statements: list[Statement]
    sitelinks: Optional[dict[str, dict[str, Any]]] = None

    model_config = ConfigDict(frozen=True)
