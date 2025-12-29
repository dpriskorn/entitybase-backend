from pydantic import BaseModel, ConfigDict
from models.internal_representation.values import Value


class Qualifier(BaseModel):
    property: str
    value: Value

    model_config = ConfigDict(frozen=True)
