import pytest

pytestmark = pytest.mark.unit

from models.internal_representation.property_metadata import (
    WikibaseDatatype,
    PropertyMetadata,
)


class TestWikibaseDatatype:
    def test_datatype_values(self) -> None:
        assert WikibaseDatatype.WIKIBASE_ITEM == "wikibase-item"
        assert WikibaseDatatype.STRING == "string"
        assert WikibaseDatatype.TIME == "time"
        assert WikibaseDatatype.QUANTITY == "quantity"
        assert WikibaseDatatype.COMMONS_MEDIA == "commonsMedia"
        assert WikibaseDatatype.EXTERNAL_ID == "external-id"
        assert WikibaseDatatype.URL == "url"

    def test_datatype_is_str_enum(self) -> None:
        assert isinstance(WikibaseDatatype.WIKIBASE_ITEM, str)
        assert WikibaseDatatype.WIKIBASE_ITEM == "wikibase-item"


class TestPropertyMetadata:
    def test_property_metadata_creation(self) -> None:
        metadata = PropertyMetadata(
            property_id="P123",
            datatype=WikibaseDatatype.WIKIBASE_ITEM,
        )
        assert metadata.property_id == "P123"
        assert metadata.datatype == WikibaseDatatype.WIKIBASE_ITEM

    def test_property_metadata_frozen(self) -> None:
        metadata = PropertyMetadata(
            property_id="P123",
            datatype=WikibaseDatatype.STRING,
        )
        with pytest.raises(Exception):  # Should raise because frozen
            metadata.property_id = "P456"
