from pydantic import ConfigDict, Field
from typing_extensions import Literal
from .base import Value


class EntitySchemaValue(Value):
    kind: Literal["entity_schema"] = Field(default="entity_schema", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#EntitySchema"

    model_config = ConfigDict(frozen=True)
