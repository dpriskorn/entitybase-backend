from pydantic import Field

from models.data.infrastructure.s3.enums import EditType
from models.data.rest_api.v1.entitybase.request.entity.entity_request_base import (
    EntityRequestBase,
)


class PreparedRequestData(EntityRequestBase):
    """Prepared request data with entity ID for entity creation."""

    id: str = Field(..., description="Entity ID (e.g., Q42)")
    type: str = Field(default="item", description="Entity type")
    edit_type: EditType = Field(
        default=EditType.UNSPECIFIED,
        description="Classification of edit type",
    )
