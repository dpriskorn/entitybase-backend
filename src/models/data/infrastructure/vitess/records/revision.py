from pydantic import BaseModel, Field


class RevisionRecord(BaseModel):
    """Revision record model."""

    statements: list = Field(default_factory=list)
    properties: list = Field(default_factory=list)
    property_counts: dict[str, int] = Field(default_factory=dict)
    labels_hashes: dict[str, str] = Field(default_factory=dict)
    descriptions_hashes: dict[str, str] = Field(default_factory=dict)
    aliases_hashes: dict[str, str] = Field(default_factory=dict)
    sitelinks_hashes: dict[str, str] = Field(default_factory=dict)


class HistoryRevisionItemRecord(BaseModel):
    """Revision record for history."""

    revision_id: int
    created_at: str = Field(default="")
    user_id: int = Field(default=0)
    edit_summary: str = Field(default="")
