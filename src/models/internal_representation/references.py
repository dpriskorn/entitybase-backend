"""Internal representation of Wikibase references."""

from pydantic import BaseModel, ConfigDict

from models.internal_representation.values import Value


class ReferenceValue(BaseModel):
    """Individual property-value pair in a reference."""

    property: str
    value: Value

    model_config = ConfigDict(frozen=True)


class Reference(BaseModel):
    """Reference providing sources for a statement."""

    hash: str
    snaks: list[ReferenceValue]

    model_config = ConfigDict(frozen=True)
