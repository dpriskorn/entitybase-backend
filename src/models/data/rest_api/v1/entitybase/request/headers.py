from typing import Annotated

from fastapi import Header
from pydantic import BaseModel, Field


class EditHeaders(BaseModel):
    """Model for required editing headers (X-User-ID and X-Edit-Summary)."""

    x_user_id: int = Field(
        ..., alias="X-User-ID", ge=0, description="User ID making the edit"
    )
    x_edit_summary: str = Field(
        ...,
        alias="X-Edit-Summary",
        min_length=1,
        max_length=200,
        description="Edit summary",
    )

    model_config = {"populate_by_name": True}


EditHeadersType = Annotated[EditHeaders, Header(convert_underscores=False)]
