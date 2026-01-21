from enum import Enum


class CanonicalizationMethod(Enum):
    URDNA2015 = "urdna2015"
    SKOLEM = "skolem"
    STRUCTURAL_HASH = "structural_hash"
