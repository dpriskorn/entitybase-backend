from typing import Annotated

from fastapi import Header
from pydantic import BaseModel, Field


class EditHeaders(BaseModel):
    """Model for editing headers (X-Edit-Summary and X-Base-Revision-ID).

    Note: X-User-ID has been removed. User identity is now determined by
    authentication credentials via the Authorization header.
    """

    x_edit_summary: str = Field(
        ...,
        alias="X-Edit-Summary",
        min_length=1,
        max_length=200,
        description="Edit summary",
    )
    x_base_revision_id: int = Field(
        default=0,
        alias="X-Base-Revision-ID",
        ge=0,
        description="Expected base revision ID for optimistic locking (0 to skip check)",
    )

    model_config = {"populate_by_name": True}


EditHeadersType = Annotated[EditHeaders, Header(convert_underscores=False)]
