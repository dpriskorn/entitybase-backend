import pytest
from io import StringIO

pytestmark = pytest.mark.unit

from models.rdf_builder.writers.property import PropertyWriter
from models.internal_representation.property_metadata import (
    PropertyMetadata,
    WikibaseDatatype,
)


class TestPropertyWriter:
    def test_write_property_item(self) -> None:
        """Test writing property with wikibase-item datatype."""
        output = StringIO()
        prop = PropertyMetadata(
            property_id="P31", datatype=WikibaseDatatype.WIKIBASE_ITEM
        )

        PropertyWriter.write_property(output, prop)

        result = output.getvalue()
        expected_lines = [
            "wd:P31 a wikibase:Property .",
            "wd:P31 wikibase:propertyType wikibase:WikibaseItem .",
            "wd:P31 wikibase:claim p:P31 .",
            "wd:P31 wikibase:statementProperty ps:P31 .",
            "wd:P31 wikibase:qualifier pq:P31 .",
            "wd:P31 wikibase:directClaim wdt:P31 .",
            "wd:P31 wikibase:reference pr:P31 .",
        ]
        for line in expected_lines:
            assert line in result

    def test_write_property_string(self) -> None:
        """Test writing property with string datatype."""
        output = StringIO()
        prop = PropertyMetadata(property_id="P123", datatype=WikibaseDatatype.STRING)

        PropertyWriter.write_property(output, prop)

        result = output.getvalue()
        assert "wd:P123 wikibase:propertyType wikibase:String ." in result

    def test_write_property_quantity(self) -> None:
        """Test writing property with quantity datatype."""
        output = StringIO()
        prop = PropertyMetadata(property_id="P456", datatype=WikibaseDatatype.QUANTITY)

        PropertyWriter.write_property(output, prop)

        result = output.getvalue()
        assert "wd:P456 wikibase:propertyType wikibase:Quantity ." in result

    def test_write_property_time(self) -> None:
        """Test writing property with time datatype."""
        output = StringIO()
        prop = PropertyMetadata(property_id="P789", datatype=WikibaseDatatype.TIME)

        PropertyWriter.write_property(output, prop)

        result = output.getvalue()
        assert "wd:P789 wikibase:propertyType wikibase:Time ." in result

    def test_write_property_commons_media(self) -> None:
        """Test writing property with commonsMedia datatype."""
        output = StringIO()
        prop = PropertyMetadata(
            property_id="P999", datatype=WikibaseDatatype.COMMONS_MEDIA
        )

        PropertyWriter.write_property(output, prop)

        result = output.getvalue()
        assert "wd:P999 wikibase:propertyType wikibase:CommonsMedia ." in result

    def test_write_property_external_id(self) -> None:
        """Test writing property with external-id datatype."""
        output = StringIO()
        prop = PropertyMetadata(
            property_id="P111", datatype=WikibaseDatatype.EXTERNAL_ID
        )

        PropertyWriter.write_property(output, prop)

        result = output.getvalue()
        assert "wd:P111 wikibase:propertyType wikibase:ExternalId ." in result

    def test_write_property_url(self) -> None:
        """Test writing property with url datatype."""
        output = StringIO()
        prop = PropertyMetadata(property_id="P222", datatype=WikibaseDatatype.URL)

        PropertyWriter.write_property(output, prop)

        result = output.getvalue()
        assert "wd:P222 wikibase:propertyType wikibase:Url ." in result

    def test_property_type_mapping(self) -> None:
        """Test _property_type method for all datatypes."""
        test_cases = [
            (WikibaseDatatype.WIKIBASE_ITEM, "WikibaseItem"),
            (WikibaseDatatype.STRING, "String"),
            (WikibaseDatatype.TIME, "Time"),
            (WikibaseDatatype.QUANTITY, "Quantity"),
            (WikibaseDatatype.COMMONS_MEDIA, "CommonsMedia"),
            (WikibaseDatatype.EXTERNAL_ID, "ExternalId"),
            (WikibaseDatatype.URL, "Url"),
        ]

        for datatype, expected in test_cases:
            prop = PropertyMetadata(property_id="P1", datatype=datatype)
            result = PropertyWriter._property_type(prop)
            assert result == expected
