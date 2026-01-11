"""Enumeration of Wikibase statement ranks."""

from enum import Enum


class Rank(str, Enum):
    PREFERRED = "preferred"
    NORMAL = "normal"
    DEPRECATED = "deprecated"
