from pydantic import BaseModel, Field


class RevisionRecord(BaseModel):
    """Revision record for history."""

    revision_id: int
    created_at: str = Field(default="")
    user_id: int = Field(default=0)
    edit_summary: str = Field(default="")