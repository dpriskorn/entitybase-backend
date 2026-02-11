"""S3 revision data model."""

from pydantic import BaseModel, ConfigDict, Field


class S3RevisionData(BaseModel):
    """Model for revision data stored in S3."""

    model_config = ConfigDict(populate_by_name=True)

    schema_version: str = Field(
        alias="schema",
        description="Schema version (MAJOR.MINOR.PATCH). Example: '1.0.0'.",
    )
    revision: dict = Field(
        description="Complete revision data including entity and metadata."
    )
    content_hash: int = Field(
        alias="hash", description="Hash of the revision content. Example: 123456789."
    )
    created_at: str = Field(
        description="Timestamp when revision was created. Example: '2023-01-01T12:00:00Z'."
    )
