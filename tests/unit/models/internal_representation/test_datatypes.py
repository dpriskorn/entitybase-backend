"""Tests for models.internal_representation.datatypes module."""

from models.internal_representation.datatypes import Datatype


class TestDatatype:
    """Test suite for Datatype enum."""

    def test_datatype_enum_values(self):
        """Test that all expected enum values are present."""
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

    def test_datatype_is_string_enum(self):
        """Test that Datatype is a string enum."""
        assert issubclass(Datatype, str)

    def test_datatype_string_comparison(self):
        """Test that enum values can be compared to strings."""
        assert Datatype.WIKIBASE_ITEM == "wikibase-item"
        assert Datatype.STRING == "string"
        assert Datatype.TIME == "time"

        assert Datatype.WIKIBASE_ITEM != "string"
        assert Datatype.STRING != "wikibase-item"

    def test_datatype_iteration(self):
        """Test that all enum values can be iterated."""
        datatypes = [d for d in Datatype]

        assert len(datatypes) == 14
        assert Datatype.WIKIBASE_ITEM in datatypes
        assert Datatype.STRING in datatypes

    def test_datatype_value_access(self):
        """Test accessing enum value."""
        datatype = Datatype.WIKIBASE_ITEM
        assert datatype.value == "wikibase-item"

    def test_datatype_from_string(self):
        """Test creating enum from string value."""
        datatype = Datatype("string")
        assert datatype == Datatype.STRING

    def test_datatype_all_values_unique(self):
        """Test that all enum values are unique."""
        values = [d.value for d in Datatype]
        assert len(values) == len(set(values))

    def test_datatype_enum_properties(self):
        """Test enum instance properties."""
        datatype = Datatype.URL

        assert isinstance(datatype, str)
        assert hasattr(datatype, "value")
