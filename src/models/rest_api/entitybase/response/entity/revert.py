"""Response models for entity revert operations."""

from pydantic import BaseModel, ConfigDict, Field


class EntityRevertResponse(BaseModel):
    """Response for entity revert operation."""

    model_config = ConfigDict(by_alias=True)

    entity_id: str = Field(description="ID of the reverted entity. Example: 'Q42'.")
    new_revision_id: int = Field(alias="new_rev_id", description="New revision ID after revert. Example: 12345.")
    reverted_from_revision_id: int = Field(alias="from_rev_id", description="Original revision ID before revert. Example: 67890.")
    reverted_at: str = Field(description="Timestamp of the revert. Example: '2023-01-01T12:00:00Z'.")
