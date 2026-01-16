from typing import Any, Dict, List

from pydantic import BaseModel, Field


class LabelValue(BaseModel):
    """Individual label entry with language and value."""

    language: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)


class DescriptionValue(BaseModel):
    """Individual description entry with language and value."""

    language: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)


class AliasValue(BaseModel):
    """Individual alias entry with language and value."""

    language: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)


class EntityLabels(BaseModel):
    """Collection of labels keyed by language code."""

    data: dict[str, LabelValue] = Field(default_factory=dict)


class EntityDescriptions(BaseModel):
    """Collection of descriptions keyed by language code."""

    data: dict[str, DescriptionValue] = Field(default_factory=dict)


class EntityAliases(BaseModel):
    """Collection of aliases keyed by language code."""

    data: dict[str, list[AliasValue]] = Field(default_factory=dict)


class EntityStatements(BaseModel):
    """List of entity statements."""

    data: list[dict[str, Any]] = Field(default_factory=list)


class EntitySitelinks(BaseModel):
    """Collection of sitelinks."""

    data: dict[str, Any] = Field(default_factory=dict)


class EntityMetadata(BaseModel):
    """Model for entity metadata."""

    id: str
    type: str = Field(default="item")
    labels: EntityLabels = Field(default_factory=lambda: EntityLabels())
    descriptions: EntityDescriptions = Field(
        default_factory=lambda: EntityDescriptions()
    )
    aliases: EntityAliases = Field(default_factory=lambda: EntityAliases())
    statements: EntityStatements = Field(default_factory=lambda: EntityStatements())
    sitelinks: EntitySitelinks = Field(default_factory=lambda: EntitySitelinks())


class WikibaseEntityResponse(BaseModel):
    """Response model for Wikibase REST API entity endpoints."""

    id: str
    type: str  # "item", "property", "lexeme"
    labels: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    descriptions: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    aliases: Dict[str, List[Dict[str, str]]] = Field(default_factory=dict)
    claims: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    sitelinks: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
