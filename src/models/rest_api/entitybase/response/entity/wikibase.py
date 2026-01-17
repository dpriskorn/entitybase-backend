from typing import Any, Dict, List

from pydantic import BaseModel, Field

from models.validation.utils import raise_validation_error


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


class SitelinkValue(BaseModel):
    """Individual sitelink entry."""

    site: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    url: str = Field(default="")


class EntityLabelsResponse(BaseModel):
    """Collection of labels keyed by language code."""

    data: dict[str, LabelValue] = Field(default_factory=dict)

    def __getitem__(self, key: str) -> LabelValue:
        return self.data[key]

    def get(self, language_code: str) -> LabelValue:
        """Get label for the specified language code."""
        if not language_code:
            raise_validation_error("Language code cannot be empty", status_code=400)
        if language_code not in self.data:
            raise_validation_error(
                f"Label not found for language {language_code}", status_code=404
            )
        return self.data[language_code]


class EntityDescriptionsResponse(BaseModel):
    """Collection of descriptions keyed by language code."""

    data: dict[str, DescriptionValue] = Field(default_factory=dict)

    def __getitem__(self, key: str) -> DescriptionValue:
        return self.data[key]

    def get(self, language_code: str) -> DescriptionValue:
        """Get description for the specified language code."""
        if not language_code:
            raise_validation_error("Language code cannot be empty", status_code=400)
        if language_code not in self.data:
            raise_validation_error(
                f"Description not found for language {language_code}", status_code=404
            )
        return self.data[language_code]


class EntityAliasesResponse(BaseModel):
    """Collection of aliases keyed by language code."""

    data: dict[str, list[AliasValue]] = Field(default_factory=dict)

    def __getitem__(self, key: str) -> list[AliasValue]:
        return self.data[key]

    def get(self, language_code: str) -> list[AliasValue]:
        """Get aliases for the specified language code."""
        if not language_code:
            raise_validation_error("Language code cannot be empty", status_code=400)
        if language_code not in self.data:
            raise_validation_error(
                f"Aliases not found for language {language_code}", status_code=404
            )
        return self.data[language_code]


class EntityStatementsResponse(BaseModel):
    """List of entity statements."""

    data: list[dict[str, Any]] = Field(default_factory=list)


class EntitySitelinksResponse(BaseModel):
    """Collection of sitelinks."""

    data: dict[str, SitelinkValue] = Field(default_factory=dict)

    def __getitem__(self, key: str) -> SitelinkValue:
        return self.data[key]

    def get(self, language_code: str) -> SitelinkValue:
        """Get sitelink for the specified language code."""
        if not language_code:
            raise_validation_error("Language code cannot be empty", status_code=400)
        if language_code not in self.data:
            raise_validation_error(
                f"Sitelink not found for language {language_code}", status_code=404
            )
        return self.data[language_code]


class EntityMetadataResponse(BaseModel):
    """Model for entity metadata."""

    id: str
    type: str = Field(default="item")
    labels: EntityLabelsResponse = Field(default_factory=lambda: EntityLabelsResponse())
    descriptions: EntityDescriptionsResponse = Field(
        default_factory=lambda: EntityDescriptionsResponse()
    )
    aliases: EntityAliasesResponse = Field(
        default_factory=lambda: EntityAliasesResponse()
    )
    statements: EntityStatementsResponse = Field(
        default_factory=lambda: EntityStatementsResponse()
    )
    sitelinks: EntitySitelinksResponse = Field(
        default_factory=lambda: EntitySitelinksResponse()
    )


class WikibaseEntityResponse(BaseModel):
    """Response model for Wikibase REST API entity endpoints."""

    id: str
    type: str  # "item", "property", "lexeme"
    labels: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    descriptions: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    aliases: Dict[str, List[Dict[str, str]]] = Field(default_factory=dict)
    claims: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    sitelinks: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
