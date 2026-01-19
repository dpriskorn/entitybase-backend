"""Entity data model."""

from typing import Any, Dict

from pydantic import BaseModel, Field


class EntityData(BaseModel):
    """Typed model for entity data in revisions."""

    id: str
    type: str
    labels: Dict[str, Any] | None = Field(default=None)
    descriptions: Dict[str, Any] | None = Field(default=None)
    aliases: Dict[str, Any] | None = Field(default=None)
    claims: Dict[str, Any] | None = Field(default=None)
    sitelinks: Dict[str, Any] | None = Field(default=None)