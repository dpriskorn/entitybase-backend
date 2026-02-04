"""Unit tests for reference_parser."""

from models.internal_representation.references import Reference
from models.json_parser.reference_parser import parse_reference, parse_references


class TestReferenceParser:
    """Unit tests for reference_parser."""

    def test_parse_reference_no_hash(self):
        """Test parsing reference without hash."""
        reference_json = {
            "snaks": {
                "P854": [
                    {
                        "snaktype": "value",
                        "property": "P854",
                        "datavalue": {
                            "value": "http://example.com",
                            "type": "string"
                        }
                    }
                ]
            }
        }

        result = parse_reference(reference_json)

        assert result.hash == ""
        assert len(result.snaks) == 1

    def test_parse_reference_multiple_snaks(self):
        """Test parsing reference with multiple snaks."""
        reference_json = {
            "hash": "def456",
            "snaks": {
                "P854": [
                    {
                        "snaktype": "value",
                        "property": "P854",
                        "datavalue": {
                            "value": "http://example.com",
                            "type": "string"
                        }
                    }
                ],
                "P813": [
                    {
                        "snaktype": "value",
                        "property": "P813",
                        "datatype": "time",
                        "datavalue": {
                            "value": {
                                "time": "+2020-01-01T00:00:00Z",
                                "timezone": 0,
                                "before": 0,
                                "after": 0,
                                "precision": 11,
                                "calendarmodel": "http://www.wikidata.org/entity/Q1985727"
                            },
                            "type": "time"
                        }
                    }
                ]
            }
        }

        result = parse_reference(reference_json)

        assert result.hash == "def456"
        assert len(result.snaks) == 2
        properties = [snak.property for snak in result.snaks]
        assert "P854" in properties
        assert "P813" in properties

    def test_parse_references_basic(self):
        """Test parsing a list of references."""
        references_json = [
            {
                "hash": "abc123",
                "snaks": {
                    "P854": [
                        {
                            "snaktype": "value",
                            "property": "P854",
                            "datavalue": {
                                "value": "http://example.com",
                                "type": "string"
                            }
                        }
                    ]
                }
            },
            {
                "hash": "def456",
                "snaks": {
                    "P813": [
                        {
                            "snaktype": "value",
                            "property": "P813",
                            "datatype": "time",
                            "datavalue": {
                                "value": {
                                    "time": "+2020-01-01T00:00:00Z",
                                    "timezone": 0,
                                    "before": 0,
                                    "after": 0,
                                    "precision": 11,
                                    "calendarmodel": "http://www.wikidata.org/entity/Q1985727"
                                },
                                "type": "time"
                            }
                        }
                    ]
                }
            }
        ]

        result = parse_references(references_json)

        assert len(result) == 2
        assert isinstance(result[0], Reference)
        assert result[0].hash == "abc123"
        assert result[1].hash == "def456"

    def test_parse_references_empty(self):
        """Test parsing empty references list."""
        result = parse_references([])
        assert result == []

    def test_parse_references_no_snaks(self):
        """Test parsing reference with no snaks."""
        references_json = [
            {
                "hash": "abc123",
                "snaks": {}
            }
        ]

        result = parse_references(references_json)

        assert len(result) == 1
        assert result[0].hash == "abc123"
        assert result[0].snaks == []
