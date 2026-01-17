from typing import Optional


from pydantic import BaseModel, Field


class EntityRedirectRequest(BaseModel):
    redirect_from_id: str = Field(
        ..., description="Source entity ID to be marked as redirect (e.g., Q59431323)"
    )
    redirect_to_id: str = Field(..., description="Target entity ID (e.g., Q42)")
    created_by: str = Field(
        default="rest-api", description="User or system creating redirect"
    )


class EntityJsonImportRequest(BaseModel):
    """Request model for importing entities from Wikidata JSONL dump."""

    jsonl_file_path: str = Field(
        ..., description="Path to JSONL file containing Wikidata entities"
    )
    start_line: int = Field(
        default=2, description="Starting line number (default 2, skips header)"
    )
    end_line: Optional[int] = Field(
        default=None, description="Ending line number (None = to end)"
    )
    overwrite_existing: bool = Field(
        default=False, description="Whether to overwrite existing entities"
    )
    worker_id: str = Field(default="", description="Worker identifier for logging")
