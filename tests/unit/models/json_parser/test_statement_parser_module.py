"""Unit tests for statement_parser."""

import pytest
from unittest.mock import MagicMock, patch

from models.json_parser.statement_parser import parse_statement
from models.internal_representation.statements import Statement
from models.internal_representation.ranks import Rank
from models.internal_representation.values.base import Value


class TestStatementParser:
    """Unit tests for statement parser."""

    def test_parse_statement_minimal(self) -> None:
        """Test parsing a minimal statement with only mainsnak."""
        with (
            patch(
                "models.json_parser.statement_parser.parse_value"
            ) as mock_parse_value,
            patch(
                "models.json_parser.statement_parser.parse_qualifiers"
            ) as mock_parse_qualifiers,
            patch(
                "models.json_parser.statement_parser.parse_references"
            ) as mock_parse_references,
        ):
            mock_value = MagicMock(spec=Value)
            mock_parse_value.return_value = mock_value
            mock_parse_qualifiers.return_value = []
            mock_parse_references.return_value = []

            statement_json = {
                "mainsnak": {
                    "property": "P31",
                    "datavalue": {"type": "wikibase-entityid", "value": {"id": "Q5"}},
                }
            }

            result = parse_statement(statement_json)

            assert isinstance(result, Statement)
            assert result.property == "P31"
            assert result.value == mock_value
            assert result.rank == Rank.NORMAL  # Default rank
            assert result.qualifiers == []
            assert result.references == []
            assert result.statement_id == ""  # Default empty

    def test_parse_statement_missing_mainsnak(self) -> None:
        """Test parsing statement with missing mainsnak."""
        with (
            patch(
                "models.json_parser.statement_parser.parse_value"
            ) as mock_parse_value,
            patch(
                "models.json_parser.statement_parser.parse_qualifiers"
            ) as mock_parse_qualifiers,
            patch(
                "models.json_parser.statement_parser.parse_references"
            ) as mock_parse_references,
        ):
            mock_value = MagicMock(spec=Value)
            mock_parse_value.return_value = mock_value
            mock_parse_qualifiers.return_value = []
            mock_parse_references.return_value = []

            statement_json = {"rank": "normal"}

            result = parse_statement(statement_json)

            assert result.property == ""  # Default empty property
            mock_parse_value.assert_called_once_with({})  # Empty mainsnak

    def test_parse_statement_different_ranks(self) -> None:
        """Test parsing statements with different ranks."""
        with (
            patch(
                "models.json_parser.statement_parser.parse_value"
            ) as mock_parse_value,
            patch(
                "models.json_parser.statement_parser.parse_qualifiers"
            ) as mock_parse_qualifiers,
            patch(
                "models.json_parser.statement_parser.parse_references"
            ) as mock_parse_references,
        ):
            mock_value = MagicMock(spec=Value)
            mock_parse_value.return_value = mock_value
            mock_parse_qualifiers.return_value = []
            mock_parse_references.return_value = []

            # Test preferred rank
            statement_json = {"mainsnak": {"property": "P31"}, "rank": "preferred"}
            result = parse_statement(statement_json)
            assert result.rank == Rank.PREFERRED

            # Test deprecated rank
            statement_json["rank"] = "deprecated"
            result = parse_statement(statement_json)
            assert result.rank == Rank.DEPRECATED

            # Test normal rank (explicit)
            statement_json["rank"] = "normal"
            result = parse_statement(statement_json)
            assert result.rank == Rank.NORMAL

    def test_parse_statement_empty_json(self) -> None:
        """Test parsing completely empty statement JSON."""
        with (
            patch(
                "models.json_parser.statement_parser.parse_value"
            ) as mock_parse_value,
            patch(
                "models.json_parser.statement_parser.parse_qualifiers"
            ) as mock_parse_qualifiers,
            patch(
                "models.json_parser.statement_parser.parse_references"
            ) as mock_parse_references,
        ):
            mock_value = MagicMock(spec=Value)
            mock_parse_value.return_value = mock_value
            mock_parse_qualifiers.return_value = []
            mock_parse_references.return_value = []

            statement_json = {}

            result = parse_statement(statement_json)

            assert result.property == ""
            assert result.rank == Rank.NORMAL
            assert result.qualifiers == []
            assert result.references == []
            assert result.statement_id == ""

    def test_parse_statement_complex_property(self) -> None:
        """Test parsing statement with complex property ID."""
        with (
            patch(
                "models.json_parser.statement_parser.parse_value"
            ) as mock_parse_value,
            patch(
                "models.json_parser.statement_parser.parse_qualifiers"
            ) as mock_parse_qualifiers,
            patch(
                "models.json_parser.statement_parser.parse_references"
            ) as mock_parse_references,
        ):
            mock_value = MagicMock(spec=Value)
            mock_parse_value.return_value = mock_value
            mock_parse_qualifiers.return_value = []
            mock_parse_references.return_value = []

            statement_json = {
                "mainsnak": {"property": "P12345"},
                "id": "Q42$complex-guid-here",
            }

            result = parse_statement(statement_json)

            assert result.property == "P12345"
            assert result.statement_id == "Q42$complex-guid-here"

    def test_parse_statement_result_immutability(self) -> None:
        """Test that parsed statement result is immutable."""
        with (
            patch(
                "models.json_parser.statement_parser.parse_value"
            ) as mock_parse_value,
            patch(
                "models.json_parser.statement_parser.parse_qualifiers"
            ) as mock_parse_qualifiers,
            patch(
                "models.json_parser.statement_parser.parse_references"
            ) as mock_parse_references,
        ):
            mock_value = MagicMock(spec=Value)
            mock_parse_value.return_value = mock_value
            mock_parse_qualifiers.return_value = []
            mock_parse_references.return_value = []

            statement_json = {"mainsnak": {"property": "P31"}}
            result = parse_statement(statement_json)

            assert isinstance(result, Statement)
            # Should not be able to modify frozen model
            with pytest.raises(Exception):  # TypeError or ValidationError
                result.property = "P32"
