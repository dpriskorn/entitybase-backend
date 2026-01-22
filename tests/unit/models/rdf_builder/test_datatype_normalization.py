"""Test CamelCase to kebab-case normalization"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
# noinspection PyPep8
from models.internal_representation.datatypes import Datatype


def test_camelcase_to_kebab_normalization() -> None:
    """Test CamelCase to kebab-case normalization"""
    # Test Wikibase prefixes
    assert Datatype.normalize_from_sparql("WikibaseItem") == "wikibase-item"
    assert Datatype.normalize_from_sparql("WikibaseString") == "wikibase-string"
    assert (
        Datatype.normalize_from_sparql("WikibaseMonolingualtext")
        == "wikibase-monolingualtext"
    )
    assert Datatype.normalize_from_sparql("WikibaseExternalId") == "external-id"
    assert Datatype.normalize_from_sparql("WikibaseUrl") == "url"
    assert Datatype.normalize_from_sparql("WikibaseProperty") == "wikibase-property"
    assert (
        Datatype.normalize_from_sparql("WikibaseMusicalNotation") == "musical-notation"
    )

    # Test without prefix (variants)
    assert Datatype.normalize_from_sparql("Item") == "item"
    assert Datatype.normalize_from_sparql("String") == "string"
    assert Datatype.normalize_from_sparql("Monolingualtext") == "monolingualtext"
    assert Datatype.normalize_from_sparql("ExternalId") == "external-id"
    assert Datatype.normalize_from_sparql("Url") == "url"
    assert Datatype.normalize_from_sparql("Property") == "property"
    assert Datatype.normalize_from_sparql("MusicalNotation") == "musical-notation"


def test_special_mappings() -> None:
    """Test special datatype mappings."""
    # Test all special mappings
    assert Datatype.normalize_from_sparql("ExternalId") == "external-id"
    assert Datatype.normalize_from_sparql("WikibaseExternalId") == "external-id"
    assert Datatype.normalize_from_sparql("Url") == "url"
    assert Datatype.normalize_from_sparql("WikibaseUrl") == "url"
    assert Datatype.normalize_from_sparql("CommonsMedia") == "commonsmedia"
    assert Datatype.normalize_from_sparql("WikibaseCommonsMedia") == "commonsmedia"
    assert Datatype.normalize_from_sparql("WikibaseEntitySchema") == "entity-schema"
    assert Datatype.normalize_from_sparql("WikibaseGeoShape") == "geo-shape"
    assert Datatype.normalize_from_sparql("WikibaseGlobeCoordinate") == "globecoordinate"
    assert Datatype.normalize_from_sparql("WikibaseTabularData") == "tabular-data"
    assert Datatype.normalize_from_sparql("WikibaseMusicalNotation") == "musical-notation"


def test_regex_normalization() -> None:
    """Test regex-based CamelCase to kebab-case conversion."""
    # Test various CamelCase patterns
    assert Datatype.normalize_from_sparql("CamelCase") == "camel-case"
    assert Datatype.normalize_from_sparql("XMLHttpRequest") == "xml-http-request"
    assert Datatype.normalize_from_sparql("SimpleTest") == "simple-test"
    assert Datatype.normalize_from_sparql("OneTwoThree") == "one-two-three"
    assert Datatype.normalize_from_sparql("ABC") == "a-b-c"
    assert Datatype.normalize_from_sparql("TestABC") == "test-a-b-c"


def test_datatype_enum_values() -> None:
    """Test that all Datatype enum values are properly defined."""
    # Test that all expected datatypes are defined
    assert Datatype.WIKIBASE_ITEM == "wikibase-item"
    assert Datatype.STRING == "string"
    assert Datatype.TIME == "time"
    assert Datatype.QUANTITY == "quantity"
    assert Datatype.GLOBOCOORDINATE == "globecoordinate"
    assert Datatype.MONOLINGUALTEXT == "monolingualtext"
    assert Datatype.EXTERNAL_ID == "external-id"
    assert Datatype.COMMONS_MEDIA == "commonsMedia"
    assert Datatype.GEO_SHAPE == "geo-shape"
    assert Datatype.TABULAR_DATA == "tabular-data"
    assert Datatype.MUSICAL_NOTATION == "musical-notation"
    assert Datatype.URL == "url"
    assert Datatype.MATH == "math"
    assert Datatype.ENTITY_SCHEMA == "entity-schema"


def test_normalization_edge_cases() -> None:
    """Test edge cases in normalization."""
    # Empty string
    assert Datatype.normalize_from_sparql("") == ""

    # Single character
    assert Datatype.normalize_from_sparql("A") == "a"

    # No uppercase letters
    assert Datatype.normalize_from_sparql("lowercase") == "lowercase"

    # Only uppercase
    assert Datatype.normalize_from_sparql("ABC") == "a-b-c"

    # Starts with uppercase
    assert Datatype.normalize_from_sparql("Test") == "test"

    # Numbers and special characters
    assert Datatype.normalize_from_sparql("Test123") == "test123"
    assert Datatype.normalize_from_sparql("Test_Value") == "test_value"


def test_wikidata_sparql_examples() -> None:
    """Test normalization with real Wikidata SPARQL examples."""
    # Examples from Wikidata SPARQL endpoint
    assert Datatype.normalize_from_sparql("WikibaseItem") == "wikibase-item"
    assert Datatype.normalize_from_sparql("String") == "string"
    assert Datatype.normalize_from_sparql("Time") == "time"
    assert Datatype.normalize_from_sparql("Quantity") == "quantity"
    assert Datatype.normalize_from_sparql("GlobeCoordinate") == "globe-coordinate"
    assert Datatype.normalize_from_sparql("Monolingualtext") == "monolingualtext"
    assert Datatype.normalize_from_sparql("ExternalId") == "external-id"
    assert Datatype.normalize_from_sparql("CommonsMedia") == "commonsmedia"
    assert Datatype.normalize_from_sparql("Url") == "url"
    assert Datatype.normalize_from_sparql("Math") == "math"


def test_case_preservation_in_special_mappings() -> None:
    """Test that special mappings preserve intended case."""
    # These should match the enum values exactly
    assert Datatype.normalize_from_sparql("WikibaseItem") == Datatype.WIKIBASE_ITEM
    assert Datatype.normalize_from_sparql("String") == Datatype.STRING
    assert Datatype.normalize_from_sparql("Time") == Datatype.TIME
    assert Datatype.normalize_from_sparql("Quantity") == Datatype.QUANTITY
    assert Datatype.normalize_from_sparql("Monolingualtext") == Datatype.MONOLINGUALTEXT
    assert Datatype.normalize_from_sparql("ExternalId") == Datatype.EXTERNAL_ID
    assert Datatype.normalize_from_sparql("Url") == Datatype.URL
    assert Datatype.normalize_from_sparql("Math") == Datatype.MATH


def test_consistency_with_enum() -> None:
    """Test that normalization is consistent with defined enum values."""
    # These should match the actual enum values
    assert Datatype.normalize_from_sparql("WikibaseItem") == "wikibase-item"
    assert Datatype.normalize_from_sparql("String") == "string"
    assert Datatype.normalize_from_sparql("Time") == "time"
    assert Datatype.normalize_from_sparql("Quantity") == "quantity"
    assert Datatype.normalize_from_sparql("Monolingualtext") == "monolingualtext"
    assert Datatype.normalize_from_sparql("ExternalId") == "external-id"
    assert Datatype.normalize_from_sparql("CommonsMedia") == "commonsmedia"
    assert Datatype.normalize_from_sparql("Url") == "url"
    assert Datatype.normalize_from_sparql("Math") == "math"


if __name__ == "__main__":
    test_camelcase_to_kebab_normalization()
    test_special_mappings()
    test_regex_normalization()
    test_datatype_enum_values()
    test_normalization_edge_cases()
    test_wikidata_sparql_examples()
    test_case_preservation_in_special_mappings()
    test_consistency_with_enum()
    print("✅ All datatype normalization tests passed!")
