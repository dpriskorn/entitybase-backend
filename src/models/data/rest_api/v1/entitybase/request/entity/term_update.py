"""Request models for term update operations."""
from pydantic import BaseModel, ConfigDict, Field


class TermUpdateRequest(BaseModel):
    """Request body for updating entity terms (labels, descriptions, representations, glosses).
    
    Matches the Wikidata internal storage format with language and value fields.
    """
    model_config = ConfigDict(extra="forbid")
    
    language: str = Field(..., min_length=2, max_length=16, description="Language code (e.g., 'en', 'fr')")
    value: str = Field(..., min_length=1, max_length=2500, description="Term text value")


class LabelUpdateRequest(BaseModel):
    """Request body for updating a label value."""

    model_config = ConfigDict(extra="forbid")

    value: str = Field(..., min_length=1, description="Label text value")


class DescriptionUpdateRequest(BaseModel):
    """Request body for updating a description value."""

    model_config = ConfigDict(extra="forbid")

    description: str = Field(..., min_length=1, description="Description text value")