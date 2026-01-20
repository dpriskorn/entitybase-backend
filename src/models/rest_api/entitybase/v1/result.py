from pydantic import BaseModel, Field


class RevisionResult(BaseModel):
    """Result of revision processing."""

    success: bool
    revision_id: int = Field(default=0)
    error: str = Field(default="")
