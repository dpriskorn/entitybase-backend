"""Unit tests for StatementHasher."""

from unittest.mock import MagicMock

from models.internal_representation.statement_hasher import StatementHasher
from models.internal_representation.statements import Statement


class TestStatementHasher:
    """Unit tests for StatementHasher."""

    def test_compute_hash_dict_input(self):
        """Test computing hash from dict input."""
        statement_dict = {
            "property": "P31",
            "value": {"kind": "entity", "value": "Q5", "datatype_uri": "http://www.wikidata.org/entity/"},
            "rank": "normal",
            "qualifiers": [],
            "references": [],
            "statement_id": "Q5$12345678-1234-1234-1234-123456789012",
        }

        hash_value = StatementHasher.compute_hash(statement_dict)

        assert isinstance(hash_value, int)
        assert hash_value > 0

    def test_compute_hash_statement_object(self):
        """Test computing hash from Statement object."""
        # Mock Statement since it's complex
        mock_statement = MagicMock(spec=Statement)
        mock_statement.model_dump.return_value = {
            "property": "P31",
            "value": {"kind": "entity", "value": "Q5", "datatype_uri": "http://www.wikidata.org/entity/"},
            "rank": "normal",
            "qualifiers": [],
            "references": [],
            "statement_id": "Q5$12345678-1234-1234-1234-123456789012",
        }

        hash_value = StatementHasher.compute_hash(mock_statement)

        assert isinstance(hash_value, int)
        assert hash_value > 0
        mock_statement.model_dump.assert_called_once()

    def test_compute_hash_excludes_statement_id(self):
        """Test that statement_id is excluded from hash."""
        statement_dict1 = {
            "property": "P31",
            "value": {"kind": "string", "value": "test", "datatype_uri": "http://www.w3.org/2001/XMLSchema#string"},
            "rank": "normal",
            "qualifiers": [],
            "references": [],
            "statement_id": "Q5$11111111-1111-1111-1111-111111111111",
        }
        statement_dict2 = {
            "property": "P31",
            "value": {"kind": "string", "value": "test", "datatype_uri": "http://www.w3.org/2001/XMLSchema#string"},
            "rank": "normal",
            "qualifiers": [],
            "references": [],
            "statement_id": "Q5$22222222-2222-2222-2222-222222222222",
        }

        hash1 = StatementHasher.compute_hash(statement_dict1)
        hash2 = StatementHasher.compute_hash(statement_dict2)

        # Hashes should be identical since only statement_id differs
        assert hash1 == hash2

    def test_compute_hash_with_qualifiers_and_references(self):
        """Test hash computation with qualifiers and references."""
        statement_dict = {
            "property": "P31",
            "value": {"kind": "entity", "value": "Q5", "datatype_uri": "http://www.wikidata.org/entity/"},
            "rank": "preferred",
            "qualifiers": [
                {"property": "P580", "value": {"kind": "time", "value": "2023-01-01", "datatype_uri": "http://www.w3.org/2001/XMLSchema#dateTime"}, "hash": 123}
            ],
            "references": [
                {"hash": "abc123", "snaks": {"P248": [{"property": "P248", "value": {"kind": "entity", "value": "Q123", "datatype_uri": "http://www.wikidata.org/entity/"}}]}}
            ],
            "statement_id": "Q5$12345678-1234-1234-1234-123456789012",
        }

        hash_value = StatementHasher.compute_hash(statement_dict)

        assert isinstance(hash_value, int)
        assert hash_value > 0

    def test_compute_hash_consistency(self):
        """Test that same input produces same hash."""
        statement_dict = {
            "property": "P31",
            "value": {"kind": "string", "value": "test", "datatype_uri": "http://www.w3.org/2001/XMLSchema#string"},
            "rank": "normal",
            "qualifiers": [],
            "references": [],
            "statement_id": "Q5$12345678-1234-1234-1234-123456789012",
        }

        hash1 = StatementHasher.compute_hash(statement_dict)
        hash2 = StatementHasher.compute_hash(statement_dict)

        assert hash1 == hash2
