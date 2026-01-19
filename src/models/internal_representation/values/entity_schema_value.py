from pydantic import ConfigDict, Field

"""Entity schema value type."""

from typing_extensions import Literal
from .base import Value


class EntitySchemaValue(Value):
    """Value representing an entity schema."""

    kind: Literal["entity_schema"] = Field(default="entity_schema", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#EntitySchema"

    model_config = ConfigDict(frozen=True)
