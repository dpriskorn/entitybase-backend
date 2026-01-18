"""Request models for removing statements."""

from pydantic import BaseModel, Field


class RemoveStatementRequest(BaseModel):
    """Request model for removing a statement."""

    edit_summary: str = Field(
        description="Summary of the edit for audit trail.",
        min_length=1
    )