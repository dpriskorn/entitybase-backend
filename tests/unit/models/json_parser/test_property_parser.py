import pytest

pytestmark = pytest.mark.unit

from models.json_parser.property_parser import parse_property
from models.internal_representation.property_metadata import WikibaseDatatype


class TestParseProperty:
    def test_parse_property_valid(self) -> None:
        """Test parsing valid property JSON."""
        entity_json = {"id": "P31", "datatype": "wikibase-item"}
        result = parse_property(entity_json)
        assert result.property_id == "P31"
        assert result.datatype == WikibaseDatatype.WIKIBASE_ITEM

    def test_parse_property_different_datatype(self) -> None:
        """Test parsing property with different datatype."""
        entity_json = {"id": "P123", "datatype": "string"}
        result = parse_property(entity_json)
        assert result.property_id == "P123"
        assert result.datatype == WikibaseDatatype.STRING

    def test_parse_property_invalid_datatype(self) -> None:
        """Test parsing property with invalid datatype raises ValueError."""
        entity_json = {"id": "P31", "datatype": "invalid-datatype"}
        with pytest.raises(ValueError):
            parse_property(entity_json)

    def test_parse_property_missing_id(self) -> None:
        """Test parsing property missing id field."""
        entity_json = {"datatype": "wikibase-item"}
        with pytest.raises(KeyError):
            parse_property(entity_json)

    def test_parse_property_missing_datatype(self) -> None:
        """Test parsing property missing datatype field."""
        entity_json = {"id": "P31"}
        with pytest.raises(KeyError):
            parse_property(entity_json)
