from pydantic import BaseModel, ConfigDict
"""Internal representation of Wikibase references."""

from models.internal_representation.values import Value

from pydantic import BaseModel, ConfigDict


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
