from pydantic import BaseModel, ConfigDict
from services.shared.models.internal_representation.values import Value


class ReferenceValue(BaseModel):
    property: str
    value: Value

    model_config = ConfigDict(frozen=True)


class Reference(BaseModel):
    hash: str
    snaks: list[ReferenceValue]

    model_config = ConfigDict(frozen=True)
