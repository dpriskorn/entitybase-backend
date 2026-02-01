"""Request models for patching statements."""

from typing import Dict, Any

from pydantic import BaseModel, Field


class PatchStatementRequest(BaseModel):
    """Request model for patching a statement."""

    claim: Dict[str, Any] = Field(
        description="The new claim data to replace the existing statement. Must be a valid Wikibase claim JSON."
    )