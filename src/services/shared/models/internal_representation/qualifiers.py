from pydantic import BaseModel, ConfigDict
from services.shared.models.internal_representation.values import Value


class Qualifier(BaseModel):
    property: str
    value: Value

    model_config = ConfigDict(frozen=True)
