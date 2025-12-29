from pydantic import ConfigDict, Field
from typing_extensions import Literal
from .base import Value


class EntityValue(Value):
    kind: Literal["entity"] = Field(default="entity", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#WikibaseItem"

    model_config = ConfigDict(frozen=True)
