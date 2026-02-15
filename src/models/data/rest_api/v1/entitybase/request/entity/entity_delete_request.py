from pydantic import BaseModel, Field

from models.data.infrastructure.s3.enums import DeleteType


class EntityDeleteRequest(BaseModel):
    """Request to delete an entity."""

    delete_type: DeleteType = Field(
        default=DeleteType.SOFT, description="Type of deletion"
    )
