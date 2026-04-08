from pydantic import BaseModel, Field


class RevisionRecord(BaseModel):
    """Revision record model."""

    statements: list = Field(default_factory=list, description="List of statement hashes in this revision")
    properties: list = Field(default_factory=list, description="List of property IDs in this revision")
    property_counts: dict[str, int] = Field(default_factory=dict, description="Property ID to count mapping")
    labels_hashes: dict[str, str] = Field(default_factory=dict, description="Label term hashes by language")
    descriptions_hashes: dict[str, str] = Field(default_factory=dict, description="Description term hashes by language")
    aliases_hashes: dict[str, str] = Field(default_factory=dict, description="Alias term hashes by language")
    sitelinks_hashes: dict[str, str] = Field(default_factory=dict, description="Sitelink hashes by site")


class HistoryRevisionItemRecord(BaseModel):
    """Revision record for history."""

    revision_id: int = Field(..., description="Revision identifier")
    created_at: str = Field(default="", description="Timestamp when revision was created")
    user_id: int = Field(default=0, description="User ID who made the revision")
    edit_summary: str = Field(default="", description="Edit summary text")
