"""Request model for adding a single statement to an entity."""

from typing import Any, Dict

from pydantic import BaseModel, Field


class AddStatementRequest(BaseModel):
    """Request model for adding a single statement to an entity, form, or sense."""

    claim: Dict[str, Any] = Field(description="A valid Wikibase statement JSON.")
