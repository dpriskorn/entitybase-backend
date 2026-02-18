from pydantic import BaseModel, ConfigDict, Field


class EntityStatusResponse(BaseModel):
    """Response model for entity status changes (lock, archive, semi-protect)."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(description="Entity ID. Example: 'Q42'.")
    revision_id: int = Field(
        alias="rev_id", description="Revision ID after status change. Example: 12345."
    )
    status: str = Field(
        description="Status that was set. Example: 'locked', 'unlocked', 'archived', 'unarchived', 'semi_protected', 'unprotected'."
    )
    idempotent: bool = Field(
        default=False,
        description="True if entity was already in the target state (no new revision created).",
    )
