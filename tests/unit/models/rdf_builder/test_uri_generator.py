"""Unit tests for uri_generator."""

import pytest

from models.rdf_builder.uri_generator import URIGenerator


class TestURIGenerator:
    """Unit tests for URIGenerator."""

    def test_default_uris(self) -> None:
        """Test default URI prefixes."""
        generator = URIGenerator()
        assert generator.wd == "http://www.wikidata.org/entity"
        assert generator.data == "https://www.wikidata.org/wiki/Special:EntityData"
        assert generator.wds == "http://www.wikidata.org/entity/statement"

    def test_entity_uri(self) -> None:
        """Test entity URI generation."""
        generator = URIGenerator()
        assert generator.entity_uri("Q42") == "http://www.wikidata.org/entity/Q42"
        assert generator.entity_uri("L123") == "http://www.wikidata.org/entity/L123"
        assert generator.entity_uri("P31") == "http://www.wikidata.org/entity/P31"

    def test_data_uri(self) -> None:
        """Test data URI generation."""
        generator = URIGenerator()
        assert generator.data_uri("Q42") == "https://www.wikidata.org/wiki/Special:EntityData/Q42"
        assert generator.data_uri("L123") == "https://www.wikidata.org/wiki/Special:EntityData/L123"

    def test_statement_uri_simple(self) -> None:
        """Test statement URI generation with simple statement ID."""
        generator = URIGenerator()
        result = generator.statement_uri("Q42$12345-6789-ABCD-EFGH-123456789ABC")
        expected = "http://www.wikidata.org/entity/statement/Q42-12345-6789-ABCD-EFGH-123456789ABC"
        assert result == expected

    def test_statement_uri_no_dollar(self) -> None:
        """Test statement URI generation with no dollar sign."""
        generator = URIGenerator()
        result = generator.statement_uri("Q42-12345-6789-ABCD-EFGH-123456789ABC")
        expected = "http://www.wikidata.org/entity/statement/Q42-12345-6789-ABCD-EFGH-123456789ABC"
        assert result == expected

    def test_statement_uri_multiple_dollars(self) -> None:
        """Test statement URI generation with multiple dollar signs."""
        generator = URIGenerator()
        result = generator.statement_uri("Q42$GUID$EXTRA")
        expected = "http://www.wikidata.org/entity/statement/Q42-GUID-EXTRA"
        assert result == expected

    def test_statement_uri_complex_guid(self) -> None:
        """Test statement URI generation with complex GUID."""
        generator = URIGenerator()
        result = generator.statement_uri("L123$F1234567-89AB-CDEF-0123-456789ABCDEF")
        expected = "http://www.wikidata.org/entity/statement/L123-F1234567-89AB-CDEF-0123-456789ABCDEF"
        assert result == expected

    def test_entity_prefixed(self) -> None:
        """Test entity prefixed URI generation."""
        assert URIGenerator.entity_prefixed("Q42") == "wd:Q42"
        assert URIGenerator.entity_prefixed("L123") == "wd:L123"
        assert URIGenerator.entity_prefixed("P31") == "wd:P31"

    def test_data_prefixed(self) -> None:
        """Test data prefixed URI generation."""
        assert URIGenerator.data_prefixed("Q42") == "data:Q42"
        assert URIGenerator.data_prefixed("L123") == "data:L123"

    def test_statement_prefixed_simple(self) -> None:
        """Test statement prefixed URI generation with simple ID."""
        result = URIGenerator.statement_prefixed("Q42$12345-6789-ABCD-EFGH-123456789ABC")
        expected = "wds:Q42-12345-6789-ABCD-EFGH-123456789ABC"
        assert result == expected

    def test_statement_prefixed_no_dollar(self) -> None:
        """Test statement prefixed URI generation with no dollar sign."""
        result = URIGenerator.statement_prefixed("Q42-12345-6789-ABCD-EFGH-123456789ABC")
        expected = "wds:Q42-12345-6789-ABCD-EFGH-123456789ABC"
        assert result == expected

    def test_statement_prefixed_multiple_dollars(self) -> None:
        """Test statement prefixed URI generation with multiple dollar signs."""
        result = URIGenerator.statement_prefixed("Q42$GUID$EXTRA")
        expected = "wds:Q42-GUID-EXTRA"
        assert result == expected

    def test_custom_base_uris(self) -> None:
        """Test URIGenerator with custom base URIs."""
        generator = URIGenerator(
            wd="https://custom.wikidata.org/entity",
            data="https://custom.wikidata.org/data",
            wds="https://custom.wikidata.org/statement"
        )

        assert generator.entity_uri("Q42") == "https://custom.wikidata.org/entity/Q42"
        assert generator.data_uri("Q42") == "https://custom.wikidata.org/data/Q42"
        result = generator.statement_uri("Q42$GUID")
        expected = "https://custom.wikidata.org/statement/Q42-GUID"
        assert result == expected

    def test_uri_generator_immutability(self) -> None:
        """Test that URIGenerator is immutable."""
        generator = URIGenerator()

        # Should be frozen (immutable)
        with pytest.raises(Exception):  # TypeError or ValidationError
            generator.wd = "modified"

    def test_statement_uri_edge_cases(self) -> None:
        """Test statement URI generation edge cases."""
        generator = URIGenerator()

        # Empty string
        assert generator.statement_uri("") == "http://www.wikidata.org/entity/statement/"

        # Only entity ID
        assert generator.statement_uri("Q42") == "http://www.wikidata.org/entity/statement/Q42"

        # Dollar at start
        result = generator.statement_uri("$GUID")
        assert result == "http://www.wikidata.org/entity/statement/-GUID"

    def test_statement_prefixed_edge_cases(self) -> None:
        """Test statement prefixed URI generation edge cases."""
        # Empty string
        assert URIGenerator.statement_prefixed("") == "wds:"

        # Only entity ID
        assert URIGenerator.statement_prefixed("Q42") == "wds:Q42"

        # Dollar at start
        assert URIGenerator.statement_prefixed("$GUID") == "wds:-GUID"

    def test_real_wikidata_guid_formats(self) -> None:
        """Test with real Wikidata GUID formats."""
        generator = URIGenerator()

        # Real Wikidata GUID format
        guid = "Q42$06e1e5e0-42ee-f89d-6780-2131e657e121"
        result = generator.statement_uri(guid)
        expected = "http://www.wikidata.org/entity/statement/Q42-06e1e5e0-42ee-f89d-6780-2131e657e121"
        assert result == expected

        prefixed_result = URIGenerator.statement_prefixed(guid)
        prefixed_expected = "wds:Q42-06e1e5e0-42ee-f89d-6780-2131e657e121"
        assert prefixed_result == prefixed_expected

    def test_lexeme_statement_uris(self) -> None:
        """Test statement URIs with lexeme IDs."""
        generator = URIGenerator()

        # Lexeme statement
        result = generator.statement_uri("L42$F1234567-89AB-CDEF-0123-456789ABCDEF")
        expected = "http://www.wikidata.org/entity/statement/L42-F1234567-89AB-CDEF-0123-456789ABCDEF"
        assert result == expected

        prefixed_result = URIGenerator.statement_prefixed("L42$F1234567-89AB-CDEF-0123-456789ABCDEF")
        prefixed_expected = "wds:L42-F1234567-89AB-CDEF-0123-456789ABCDEF"
        assert prefixed_result == prefixed_expected