"""Edit context model for entity operations."""

from pydantic import BaseModel, Field


class EditContext(BaseModel):
    """Context for an edit operation."""

    user_id: int = Field(..., description="User performing the edit")
    edit_summary: str = Field(..., description="Edit summary/description")
