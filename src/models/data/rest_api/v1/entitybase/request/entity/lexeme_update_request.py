from pydantic import Field

from models.data.infrastructure.s3.enums import EditType
from models.data.rest_api.v1.entitybase.request.entity.entity_request_base import (
    EntityRequestBase,
)


class LexemeUpdateRequest(EntityRequestBase):
    """Request model for updating a lexeme entity."""

    type: str = Field(default="lexeme", description="Entity type")
    edit_type: EditType = Field(
        default=EditType.UNSPECIFIED,
        description="Classification of edit type",
    )
    is_not_autoconfirmed_user: bool = Field(
        default=False, description="User is not autoconfirmed (new/unconfirmed account)"
    )
