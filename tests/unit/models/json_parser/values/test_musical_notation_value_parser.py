"""Unit tests for musical_notation_value_parser."""

import pytest

from models.json_parser.values.musical_notation_value_parser import (
    parse_musical_notation_value,
)
from models.internal_representation.values.musical_notation_value import (
    MusicalNotationValue,
)


class TestMusicalNotationValueParser:
    """Unit tests for musical notation value parser."""

    def test_parse_valid_musical_notation_value(self):
        """Test parsing a valid musical notation value."""
        datavalue = {"value": "\\relative c' { c d e f | g a b c }"}

        result = parse_musical_notation_value(datavalue)

        assert isinstance(result, MusicalNotationValue)
        assert result.kind == "musical_notation"
        assert result.value == "\\relative c' { c d e f | g a b c }"
        assert result.datatype_uri == "http://wikiba.se/ontology#MusicalNotation"

    def test_parse_musical_notation_value_simple_notation(self):
        """Test parsing simple musical notation."""
        datavalue = {"value": "C D E F G"}

        result = parse_musical_notation_value(datavalue)

        assert result.value == "C D E F G"

    def test_parse_musical_notation_value_complex_lilypond(self):
        """Test parsing complex LilyPond notation."""
        datavalue = {
            "value": "\\score { \\new Staff { \\clef treble \\time 4/4 c'4 d' e' f' } }"
        }

        result = parse_musical_notation_value(datavalue)

        assert (
            result.value
            == "\\score { \\new Staff { \\clef treble \\time 4/4 c'4 d' e' f' } }"
        )

    def test_parse_musical_notation_value_empty_string(self):
        """Test parsing an empty musical notation value."""
        datavalue = {"value": ""}

        result = parse_musical_notation_value(datavalue)

        assert result.value == ""

    def test_parse_musical_notation_value_missing_value(self):
        """Test parsing when the value field is missing."""
        datavalue = {}

        result = parse_musical_notation_value(datavalue)

        assert isinstance(result, MusicalNotationValue)
        assert result.value == ""  # Empty string default

    def test_parse_musical_notation_value_abc_notation(self):
        """Test parsing ABC musical notation."""
        datavalue = {"value": "X:1\\nT:Example\\nM:4/4\\nK:C\\nC D E F | G A B c |"}

        result = parse_musical_notation_value(datavalue)

        assert result.value == "X:1\\nT:Example\\nM:4/4\\nK:C\\nC D E F | G A B c |"

    def test_parse_musical_notation_value_unicode_symbols(self):
        """Test parsing musical notation with unicode musical symbols."""
        datavalue = {"value": "♪ ♫ ♪ C ♭ D ♯ E ♮ ♪"}

        result = parse_musical_notation_value(datavalue)

        assert result.value == "♪ ♫ ♪ C ♭ D ♯ E ♮ ♪"

    def test_parse_musical_notation_value_result_immutability(self):
        """Test that the parsed result is immutable (frozen model)."""
        datavalue = {"value": "\\relative c { c d e f }"}

        result = parse_musical_notation_value(datavalue)

        assert isinstance(result, MusicalNotationValue)
        # Should not be able to modify frozen model
        with pytest.raises(Exception):  # TypeError or ValidationError
            result.value = "modified"

    def test_parse_musical_notation_value_long_notation(self):
        """Test parsing a very long musical notation string."""
        long_notation = "\\score { \\new PianoStaff << \\new Staff { \\clef treble c'4 d' e' f' g' a' b' c'' } \\new Staff { \\clef bass c4 d e f g a b c' } >> }"
        datavalue = {"value": long_notation}

        result = parse_musical_notation_value(datavalue)

        assert result.value == long_notation
