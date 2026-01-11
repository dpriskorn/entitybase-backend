# src/models/internal_representation/property_metadata.py

"""Property metadata and datatype definitions."""

from enum import Enum

from pydantic import BaseModel, ConfigDict


class WikibaseDatatype(str, Enum):
    WIKIBASE_ITEM = "wikibase-item"
    STRING = "string"
    TIME = "time"
    QUANTITY = "quantity"
    COMMONS_MEDIA = "commonsMedia"
    EXTERNAL_ID = "external-id"
    URL = "url"


class PropertyMetadata(BaseModel):
    property_id: str
    datatype: WikibaseDatatype

    model_config = ConfigDict(frozen=True)
