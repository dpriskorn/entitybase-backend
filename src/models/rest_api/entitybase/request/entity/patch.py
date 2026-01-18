from typing import List, Dict, Any

from pydantic import BaseModel, Field


class JsonPatchOperation(BaseModel):
    """A single JSON Patch operation."""

    op: str = Field(description="Operation type: add, remove, replace, etc.")
    path: str = Field(description="JSON Pointer path to the target")
    value: Any = Field(default=None, description="Value for add/replace operations")
    from_: str = Field(
        default="", alias="from", description="Source path for move/copy"
    )


class BasePatchRequest(BaseModel):
    """Base request for patch operations."""

    edit_summary: str = Field(
        min_length=1, max_length=200, description="Edit summary for this change"
    )
    patch: JsonPatchOperation = Field(description="Single JSON Patch operation")


class LabelPatchRequest(BasePatchRequest):
    """Request to patch entity labels."""

    pass


class DescriptionPatchRequest(BasePatchRequest):
    """Request to patch entity descriptions."""

    pass


class AliasPatchRequest(BasePatchRequest):
    """Request to patch entity aliases."""

    pass


class ClaimPatchRequest(BasePatchRequest):
    """Request to patch claims for a specific property."""

    pass


class SitelinkPatchRequest(BasePatchRequest):
    """Request to patch sitelinks."""

    pass


class StatePatchRequest(BasePatchRequest):
    """Request to patch entity state."""

    pass
