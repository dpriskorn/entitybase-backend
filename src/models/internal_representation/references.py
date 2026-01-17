"""Internal representation of Wikibase references."""

from pydantic import BaseModel, ConfigDict, Field

from models.internal_representation.values.base import Value


class ReferenceValue(BaseModel):
    """Individual property-value pair in a reference."""

    property: str
    value: Value

    model_config = ConfigDict(frozen=True)


class Reference(BaseModel):
    """Reference providing sources for a statement."""

    hash: str
    snaks: list[ReferenceValue] = Field(default_factory=list)

    model_config = ConfigDict(frozen=True)
