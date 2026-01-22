"""Unit tests for datatypes."""

from models.internal_representation.datatypes import Datatype


class TestDatatypes:
    """Unit tests for Datatype enum and methods."""

    def test_datatype_enum_values(self):
        """Test that Datatype enum has expected values."""
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

    def test_normalize_from_sparql_special_mappings(self):
        """Test normalize_from_sparql with special mappings."""
        # Test each special mapping
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

    def test_normalize_from_sparql_regex_conversion(self):
        """Test normalize_from_sparql with regex conversion."""
        # Test cases that use regex
        assert Datatype.normalize_from_sparql("WikibaseItem") == "wikibase-item"
        assert Datatype.normalize_from_sparql("String") == "string"
        assert Datatype.normalize_from_sparql("Time") == "time"
        assert Datatype.normalize_from_sparql("Quantity") == "quantity"
        assert Datatype.normalize_from_sparql("GlobeCoordinate") == "globecoordinate"
        assert Datatype.normalize_from_sparql("MonolingualText") == "monolingual-text"
        assert Datatype.normalize_from_sparql("Math") == "math"

    def test_normalize_from_sparql_already_kebab(self):
        """Test normalize_from_sparql with already kebab-case strings."""
        assert Datatype.normalize_from_sparql("wikibase-item") == "wikibase-item"
        assert Datatype.normalize_from_sparql("external-id") == "external-id"
        assert Datatype.normalize_from_sparql("url") == "url"

    def test_normalize_from_sparql_edge_cases(self):
        """Test normalize_from_sparql with edge cases."""
        # Empty string
        assert Datatype.normalize_from_sparql("") == ""

        # Single word
        assert Datatype.normalize_from_sparql("Word") == "word"

        # Multiple transitions
        assert Datatype.normalize_from_sparql("CamelCaseExample") == "camel-case-example"

        # Starting with lowercase
        assert Datatype.normalize_from_sparql("camelCase") == "camel-case"

        # Numbers
        assert Datatype.normalize_from_sparql("Type123Value") == "type123-value"
