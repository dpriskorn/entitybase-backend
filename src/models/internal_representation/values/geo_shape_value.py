from pydantic import ConfigDict, Field
from typing_extensions import Literal
from .base import Value


class GeoShapeValue(Value):
    kind: Literal["geo_shape"] = Field(default="geo_shape", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#GeoShape"

    model_config = ConfigDict(frozen=True)
