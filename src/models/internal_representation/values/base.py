from typing import Any, Literal

"""Base class for Wikibase data values."""

from pydantic import BaseModel, ConfigDict


class Value(BaseModel):
    """Base class for all Wikibase data values."""

    kind: Literal[
        "entity",
        "string",
        "time",
        "quantity",
        "globe",
        "monolingual",
        "external_id",
        "commons_media",
        "geo_shape",
        "tabular_data",
        "musical_notation",
        "url",
        "math",
        "entity_schema",
        "novalue",
        "somevalue",
    ]
    value: Any
    datatype_uri: str

    model_config = ConfigDict(frozen=True)
