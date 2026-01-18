"""Request models for adding properties to entities."""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class AddPropertyRequest(BaseModel):
    """Request model for adding claims to a single property."""

    claims: List[Dict[str, Any]] = Field(
        description="List of claim statements for the property. Each claim should be a valid Wikibase statement JSON."
    )
    edit_summary: str = Field(
        description="Summary of the edit for audit trail.",
        min_length=1
    )