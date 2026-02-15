from pydantic import Field

from models.data.infrastructure.s3.enums import EditType
from models.data.rest_api.v1.entitybase.request.entity.entity_request_base import (
    EntityRequestBase,
)


class EntityCreateRequest(EntityRequestBase):
    """Request model for entity creation."""

    type: str = Field(..., description="Entity type (item, property, lexeme)")
    edit_type: EditType = Field(
        default=EditType.UNSPECIFIED,
        description="Classification of edit type",
    )
