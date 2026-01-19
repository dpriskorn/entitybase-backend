"""Internal data models for entity representation."""

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from models.internal_representation.statements import Statement
from models.rest_api.entitybase.response.entity import EntitySitelinksResponse

if TYPE_CHECKING:
    pass


class EntityData(BaseModel):
    """Internal data model for entity with nested structures."""

    id: str
    type: str  # Simplified, or use EntityType
    labels: dict[str, dict[str, str]]  # e.g., {"en": {"language": "en", "value": "Test"}}
    descriptions: dict[str, dict[str, str]]
    aliases: dict[str, list[dict[str, str]]]
    statements: list[Statement]
    sitelinks: dict[str, str] | None = Field(default=None)  # Simplified sitelinks

    model_config = {"frozen": True}</content>
<parameter name="filePath">src/models/internal_representation/entity_data.py