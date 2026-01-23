import logging

"""Enumeration of Wikibase datatype identifiers."""

from enum import Enum

logger = logging.getLogger(__name__)


class Datatype(str, Enum):
    WIKIBASE_ITEM = "wikibase-item"
    STRING = "string"
    TIME = "time"
    QUANTITY = "quantity"
    GLOBOCOORDINATE = "globecoordinate"
    MONOLINGUALTEXT = "monolingualtext"
    EXTERNAL_ID = "external-id"
    COMMONS_MEDIA = "commonsMedia"
    GEO_SHAPE = "geo-shape"
    TABULAR_DATA = "tabular-data"
    MUSICAL_NOTATION = "musical-notation"
    URL = "url"
    MATH = "math"
    ENTITY_SCHEMA = "entity-schema"
