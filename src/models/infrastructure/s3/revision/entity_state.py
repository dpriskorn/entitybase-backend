"""Entity state model."""

from pydantic import BaseModel, ConfigDict, Field


class EntityState(BaseModel):
    """Model for entity state information."""

    model_config = ConfigDict(populate_by_name=True)

    is_semi_protected: bool = Field(
        alias="sp",
        default=False,
        description="Whether the entity is semi-protected. Example: true.",
    )
    is_locked: bool = Field(
        alias="locked",
        default=False,
        description="Whether the entity is locked. Example: false.",
    )
    is_archived: bool = Field(
        default=False,
        alias="archived",
        description="Whether the entity is archived. Example: false.",
    )
    is_dangling: bool = Field(
        default=False,
        alias="dangling",
        description="Whether the entity is dangling. Example: false.",
    )
    is_mass_edit_protected: bool = Field(
        default=False,
        alias="mep",
        description="Whether the entity has mass edit protection. Example: true.",
    )
    is_deleted: bool = Field(
        default=False,
        alias="deleted",
        description="Whether the entity is deleted. Example: true.",
    )