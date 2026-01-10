from models.internal_representation.statement_backlink_extractor import (
    StatementBacklinkExtractor,
)


class TestStatementBacklinkExtractor:
    def test_extract_backlink_data_mainsnak_item(self) -> None:
        """Test extraction from mainsnak with item reference."""
        statement = {
            "mainsnak": {
                "snaktype": "value",
                "property": "P31",
                "datatype": "wikibase-item",
                "datavalue": {
                    "value": {"entity-type": "item", "id": "Q5"},
                    "type": "wikibase-entityid",
                },
            },
            "type": "statement",
            "rank": "normal",
            "qualifiers": {},
            "references": [],
        }
        result = StatementBacklinkExtractor.extract_backlink_data(statement)
        assert result == [("Q5", "P31", "normal")]

    def test_extract_backlink_data_mainsnak_property(self) -> None:
        """Test extraction from mainsnak with property reference."""
        statement = {
            "mainsnak": {
                "snaktype": "value",
                "property": "P31",
                "datatype": "wikibase-property",
                "datavalue": {
                    "value": {"entity-type": "property", "id": "P17"},
                    "type": "wikibase-entityid",
                },
            },
            "type": "statement",
            "rank": "preferred",
            "qualifiers": {},
            "references": [],
        }
        result = StatementBacklinkExtractor.extract_backlink_data(statement)
        assert result == [("P17", "P31", "preferred")]

    def test_extract_backlink_data_qualifiers(self) -> None:
        """Test extraction from qualifiers."""
        statement = {
            "mainsnak": {
                "snaktype": "value",
                "property": "P31",
                "datavalue": {
                    "value": {"entity-type": "item", "id": "Q5"},
                    "type": "wikibase-entityid",
                },
            },
            "type": "statement",
            "rank": "normal",
            "qualifiers": {
                "P580": [
                    {
                        "snaktype": "value",
                        "property": "P580",
                        "datavalue": {
                            "value": {"entity-type": "item", "id": "Q10"},
                            "type": "wikibase-entityid",
                        },
                    }
                ]
            },
            "references": [],
        }
        result = StatementBacklinkExtractor.extract_backlink_data(statement)
        expected = [("Q5", "P31", "normal"), ("Q10", "P580", "normal")]
        assert result == expected

    def test_extract_backlink_data_references(self) -> None:
        """Test extraction from references."""
        statement = {
            "mainsnak": {
                "snaktype": "value",
                "property": "P31",
                "datavalue": {
                    "value": {"entity-type": "item", "id": "Q5"},
                    "type": "wikibase-entityid",
                },
            },
            "type": "statement",
            "rank": "normal",
            "qualifiers": {},
            "references": [
                {
                    "snaks": {
                        "P248": [
                            {
                                "snaktype": "value",
                                "property": "P248",
                                "datavalue": {
                                    "value": {"entity-type": "item", "id": "Q15"},
                                    "type": "wikibase-entityid",
                                },
                            }
                        ]
                    }
                }
            ],
        }
        result = StatementBacklinkExtractor.extract_backlink_data(statement)
        expected = [("Q5", "P31", "normal"), ("Q15", "P248", "normal")]
        assert result == expected

    def test_extract_backlink_data_no_references(self) -> None:
        """Test statement with no entity references."""
        statement = {
            "mainsnak": {
                "snaktype": "value",
                "property": "P31",
                "datavalue": {
                    "value": "some string",
                    "type": "string",
                },
            },
            "type": "statement",
            "rank": "normal",
            "qualifiers": {},
            "references": [],
        }
        result = StatementBacklinkExtractor.extract_backlink_data(statement)
        assert result == []

    def test_extract_backlink_data_invalid_entity_type(self) -> None:
        """Test that invalid entity types are ignored."""
        statement = {
            "mainsnak": {
                "snaktype": "value",
                "property": "P31",
                "datavalue": {
                    "value": {"entity-type": "invalid", "id": "Q5"},
                    "type": "wikibase-entityid",
                },
            },
            "type": "statement",
            "rank": "normal",
            "qualifiers": {},
            "references": [],
        }
        result = StatementBacklinkExtractor.extract_backlink_data(statement)
        assert result == []

    def test_extract_backlink_data_missing_rank(self) -> None:
        """Test default rank when missing."""
        statement = {
            "mainsnak": {
                "snaktype": "value",
                "property": "P31",
                "datavalue": {
                    "value": {"entity-type": "item", "id": "Q5"},
                    "type": "wikibase-entityid",
                },
            },
            "type": "statement",
            # rank missing
            "qualifiers": {},
            "references": [],
        }
        result = StatementBacklinkExtractor.extract_backlink_data(statement)
        assert result == [("Q5", "P31", "normal")]

    def test_extract_backlink_data_deprecated_rank(self) -> None:
        """Test deprecated rank."""
        statement = {
            "mainsnak": {
                "snaktype": "value",
                "property": "P31",
                "datavalue": {
                    "value": {"entity-type": "item", "id": "Q5"},
                    "type": "wikibase-entityid",
                },
            },
            "type": "statement",
            "rank": "deprecated",
            "qualifiers": {},
            "references": [],
        }
        result = StatementBacklinkExtractor.extract_backlink_data(statement)
        assert result == [("Q5", "P31", "deprecated")]
