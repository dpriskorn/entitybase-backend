"""Unit tests for triple."""

import io
from unittest.mock import MagicMock, patch

import pytest

from models.rdf_builder.models.rdf_statement import RDFStatement
from models.rdf_builder.property_registry.models import PropertyShape, PropertyPredicates
from models.rdf_builder.property_registry.registry import PropertyRegistry
from models.rdf_builder.writers.triple import TripleWriters


class TestTripleWriters:
    """Unit tests for TripleWriters."""

    def test_write_header(self) -> None:
        """Test writing Turtle header with prefixes."""
        output = io.StringIO()
        TripleWriters.write_header(output)

        result = output.getvalue()
        assert "@prefix wd:" in result
        assert "@prefix wdt:" in result
        assert "@prefix wikibase:" in result
        assert "@prefix rdfs:" in result

    def test_write_entity_type(self) -> None:
        """Test writing entity type triple."""
        output = io.StringIO()
        TripleWriters.write_entity_type(output, "Q42")

        result = output.getvalue()
        assert result == "wd:Q42 a wikibase:Item .\n"

    def test_write_dataset_triples(self) -> None:
        """Test writing dataset triples for entity."""
        output = io.StringIO()
        TripleWriters.write_dataset_triples(output, "Q42")

        result = output.getvalue()
        assert "sdc:Q42 a schema:Dataset ." in result
        assert "sdc:Q42 schema:about wd:Q42 ." in result
        assert "sdc:Q42 cc:license <http://creativecommons.org/publicdomain/zero/1.0/> ." in result

    def test_write_label(self) -> None:
        """Test writing label triple."""
        output = io.StringIO()
        TripleWriters.write_label(output, "Q42", "en", "Douglas Adams")

        result = output.getvalue()
        assert result == 'wd:Q42 rdfs:label "Douglas Adams"@en .\n'

    def test_write_description(self) -> None:
        """Test writing description triple."""
        output = io.StringIO()
        TripleWriters.write_description(output, "Q42", "en", "English writer")

        result = output.getvalue()
        assert result == 'wd:Q42 schema:description "English writer"@en .\n'

    def test_write_alias(self) -> None:
        """Test writing alias triple."""
        output = io.StringIO()
        TripleWriters.write_alias(output, "Q42", "en", "DNA")

        result = output.getvalue()
        assert result == 'wd:Q42 skos:altLabel "DNA"@en .\n'

    def test_write_sitelink(self) -> None:
        """Test writing sitelink triple."""
        output = io.StringIO()
        sitelink_data = {"site": "enwiki", "title": "Douglas Adams"}
        TripleWriters.write_sitelink(output, "Q42", sitelink_data)

        result = output.getvalue()
        expected = "wd:Q42 schema:sameAs <https://enwiki.wikipedia.org/wiki/Douglas_Adams> .\n"
        assert result == expected

    def test_write_sitelink_with_spaces(self) -> None:
        """Test writing sitelink with spaces in title."""
        output = io.StringIO()
        sitelink_data = {"site": "enwiki", "title": "Douglas Adams"}
        TripleWriters.write_sitelink(output, "Q42", sitelink_data)

        result = output.getvalue()
        assert "Douglas_Adams" in result  # Spaces converted to underscores

    def test_write_redirect(self) -> None:
        """Test writing redirect triple."""
        output = io.StringIO()
        TripleWriters.write_redirect(output, "Q123", "Q456")

        result = output.getvalue()
        assert result == "wd:Q123 owl:sameAs wd:Q456 .\n"

    def test_write_direct_claim(self) -> None:
        """Test writing direct claim triple."""
        output = io.StringIO()
        TripleWriters.write_direct_claim(output, "Q42", "P31", "wd:Q5")

        result = output.getvalue()
        assert result == "wd:Q42 wdt:P31 wd:Q5 .\n"

    def test_needs_value_node(self) -> None:
        """Test _needs_value_node method."""
        # Test with value objects that have kind attribute
        mock_time_value = MagicMock()
        mock_time_value.kind = "time"
        assert TripleWriters._needs_value_node(mock_time_value) is True

        mock_quantity_value = MagicMock()
        mock_quantity_value.kind = "quantity"
        assert TripleWriters._needs_value_node(mock_quantity_value) is True

        mock_globe_value = MagicMock()
        mock_globe_value.kind = "globe"
        assert TripleWriters._needs_value_node(mock_globe_value) is True

        # Test with values that don't need value nodes
        mock_string_value = MagicMock()
        mock_string_value.kind = "string"
        assert TripleWriters._needs_value_node(mock_string_value) is False

        mock_entity_value = MagicMock()
        mock_entity_value.kind = "entity"
        assert TripleWriters._needs_value_node(mock_entity_value) is False

        # Test with objects that don't have kind attribute
        plain_value = "plain string"
        assert TripleWriters._needs_value_node(plain_value) is False

    @patch('models.rdf_builder.writers.triple.ValueFormatter.format_value')
    @patch('models.rdf_builder.writers.triple.ValueNodeWriter.write_time_value_node')
    @patch('models.rdf_builder.writers.triple.generate_value_node_uri')
    def test_write_statement_with_time_value_node(self, mock_gen_uri, mock_write_node, mock_format_value) -> None:
        """Test writing statement with time value that needs a value node."""
        output = io.StringIO()

        # Mock time value
        mock_time_value = MagicMock()
        mock_time_value.kind = "time"

        # Mock RDF statement
        rdf_statement = RDFStatement(
            guid="Q42$GUID123",
            property_id="P569",
            value=mock_time_value,
            rank="normal",
            qualifiers=[],
            references=[]
        )

        # Mock property shape
        shape = PropertyShape(
            pid="P569",
            datatype="time",
            predicates=PropertyPredicates(
                direct="wdt:P569",
                statement="ps:P569",
                qualifier="pq:P569",
                reference="pr:P569",
                value_node="psv:P569"
            )
        )

        mock_gen_uri.return_value = "TIME123"
        mock_format_value.return_value = '"1952-03-11"^^xsd:dateTime'

        # Mock property registry
        mock_registry = PropertyRegistry(properties={})

        TripleWriters.write_statement(output, "Q42", rdf_statement, shape, mock_registry)

        result = output.getvalue()

        # Should link to value node
        assert "ps:P569 wdv:TIME123 ." in result
        assert "a wikibase:Statement, wikibase:BestRank ." in result
        assert "wikibase:rank wikibase:NormalRank ." in result

        # Should write direct claim
        assert "wd:Q42 wdt:P569" in result

        # Should call value node writer
        mock_write_node.assert_called_once_with(output, "TIME123", mock_time_value, None)

    @patch('models.rdf_builder.writers.triple.ValueFormatter.format_value')
    def test_write_statement_simple_value(self, mock_format_value) -> None:
        """Test writing statement with simple value (no value node needed)."""
        output = io.StringIO()

        # Mock string value
        mock_string_value = MagicMock()
        mock_string_value.kind = "string"

        # Mock RDF statement
        rdf_statement = RDFStatement(
            guid="Q42$GUID123",
            property_id="P1476",
            value=mock_string_value,
            rank="preferred",
            qualifiers=[],
            references=[]
        )

        # Mock property shape
        shape = PropertyShape(
            pid="P1476",
            datatype="monolingualtext",
            predicates=PropertyPredicates(
                direct="wdt:P1476",
                statement="ps:P1476",
                qualifier="pq:P1476",
                reference="pr:P1476"
            )
        )

        mock_format_value.return_value = '"The Hitchhiker\'s Guide"@en'

        # Mock property registry
        mock_registry = PropertyRegistry(properties={})

        TripleWriters.write_statement(output, "Q42", rdf_statement, shape, mock_registry)

        result = output.getvalue()

        # Should write simple statement value
        assert 'ps:P1476 "The Hitchhiker\'s Guide"@en .' in result
        assert "a wikibase:Statement ." in result  # Preferred rank doesn't get BestRank
        assert "wikibase:rank wikibase:PreferredRank ." in result

    def test_write_statement_deprecated_rank(self) -> None:
        """Test writing statement with deprecated rank."""
        output = io.StringIO()

        # Mock RDF statement with deprecated rank
        rdf_statement = RDFStatement(
            guid="Q42$GUID123",
            property_id="P31",
            value="wd:Q5",
            rank="deprecated",
            qualifiers=[],
            references=[]
        )

        # Mock property shape
        shape = PropertyShape(
            pid="P31",
            datatype="wikibase-item",
            predicates=PropertyPredicates(
                direct="wdt:P31",
                statement="ps:P31",
                qualifier="pq:P31",
                reference="pr:P31"
            )
        )

        # Mock property registry
        mock_registry = PropertyRegistry(properties={})

        with patch('models.rdf_builder.writers.triple.ValueFormatter.format_value', return_value="wd:Q5"):
            TripleWriters.write_statement(output, "Q42", rdf_statement, shape, mock_registry)

        result = output.getvalue()
        assert "wikibase:rank wikibase:DeprecatedRank ." in result

    @patch('models.rdf_builder.writers.triple.ValueFormatter.format_value')
    @patch('models.rdf_builder.writers.triple.ValueNodeWriter.write_quantity_value_node')
    @patch('models.rdf_builder.writers.triple.generate_value_node_uri')
    def test_write_statement_with_qualifier_value_node(self, mock_gen_uri, mock_write_node, mock_format_value) -> None:
        """Test writing statement with qualifier that needs value node."""
        output = io.StringIO()

        # Mock qualifier with quantity value
        mock_qualifier_value = MagicMock()
        mock_qualifier_value.kind = "quantity"

        qualifier = MagicMock()
        qualifier.value = mock_qualifier_value
        qualifier.property = "P1107"

        # Mock RDF statement
        rdf_statement = RDFStatement(
            guid="Q42$GUID123",
            property_id="P31",
            value="wd:Q5",
            rank="normal",
            qualifiers=[qualifier],
            references=[]
        )

        # Mock property shape
        shape = PropertyShape(
            pid="P31",
            datatype="wikibase-item",
            predicates=PropertyPredicates(
                direct="wdt:P31",
                statement="ps:P31",
                qualifier="pq:P31",
                qualifier_value="pqv:P31",
                reference="pr:P31"
            )
        )

        mock_gen_uri.return_value = "QUANT123"
        mock_format_value.return_value = "wd:Q5"

        # Mock property registry
        mock_registry = PropertyRegistry(properties={})

        TripleWriters.write_statement(output, "Q42", rdf_statement, shape, mock_registry)

        result = output.getvalue()

        # Should link qualifier to value node
        assert "pqv:P31 wdv:QUANT123 ." in result

        # Should call value node writer for qualifier
        mock_write_node.assert_called_once_with(output, "QUANT123", mock_qualifier_value, None)

    @patch('models.rdf_builder.writers.triple.ValueFormatter.format_value')
    def test_write_statement_with_simple_qualifier(self, mock_format_value) -> None:
        """Test writing statement with simple qualifier (no value node)."""
        output = io.StringIO()

        # Mock qualifier with string value
        mock_qualifier_value = MagicMock()
        mock_qualifier_value.kind = "string"

        qualifier = MagicMock()
        qualifier.value = mock_qualifier_value
        qualifier.property = "P1476"

        # Mock RDF statement
        rdf_statement = RDFStatement(
            guid="Q42$GUID123",
            property_id="P31",
            value="wd:Q5",
            rank="normal",
            qualifiers=[qualifier],
            references=[]
        )

        # Mock property shape
        shape = PropertyShape(
            pid="P31",
            datatype="wikibase-item",
            predicates=PropertyPredicates(
                direct="wdt:P31",
                statement="ps:P31",
                qualifier="pq:P31",
                reference="pr:P31"
            )
        )

        mock_format_value.side_effect = ["wd:Q5", '"Book Title"@en']

        # Mock property registry
        mock_registry = PropertyRegistry(properties={})

        TripleWriters.write_statement(output, "Q42", rdf_statement, shape, mock_registry)

        result = output.getvalue()

        # Should write simple qualifier
        assert 'pq:P31 "Book Title"@en .' in result

    @patch('models.rdf_builder.writers.triple.ValueFormatter.format_value')
    def test_write_statement_with_references(self, mock_format_value) -> None:
        """Test writing statement with references."""
        output = io.StringIO()

        # Mock reference snak
        mock_snak_value = MagicMock()
        mock_snak_value.kind = "string"

        snak = MagicMock()
        snak.value = mock_snak_value
        snak.property = "P854"

        reference = MagicMock()
        reference.snaks = [snak]

        # Mock RDF statement
        rdf_statement = RDFStatement(
            guid="Q42$GUID123",
            property_id="P31",
            value="wd:Q5",
            rank="normal",
            qualifiers=[],
            references=[reference]
        )

        # Mock property shape
        shape = PropertyShape(
            pid="P31",
            datatype="wikibase-item",
            predicates=PropertyPredicates(
                direct="wdt:P31",
                statement="ps:P31",
                qualifier="pq:P31",
                reference="pr:P31"
            )
        )

        mock_format_value.side_effect = ["wd:Q5", '"https://example.com"']

        # Mock property registry and RDF reference
        mock_registry = MagicMock()
        mock_snak_shape = MagicMock()
        mock_snak_shape.predicates.reference = "pr:P854"
        mock_registry.shape.return_value = mock_snak_shape

        with patch('models.rdf_builder.models.rdf_reference.RDFReference') as mock_rdf_ref_class:
            mock_rdf_ref = MagicMock()
            mock_rdf_ref.reference_uri = "wdref:123"
            mock_rdf_ref_class.return_value = mock_rdf_ref

            TripleWriters.write_statement(output, "Q42", rdf_statement, shape, mock_registry)

        result = output.getvalue()

        # Should write reference link
        assert "prov:wasDerivedFrom wdref:123 ." in result
        # Should write reference snak
        assert 'pr:P854 "https://example.com" .' in result

    def test_write_statement_empty_qualifiers_references(self) -> None:
        """Test writing statement with no qualifiers or references."""
        output = io.StringIO()

        # Mock RDF statement with empty lists
        rdf_statement = RDFStatement(
            guid="Q42$GUID123",
            property_id="P31",
            value="wd:Q5",
            rank="normal",
            qualifiers=[],
            references=[]
        )

        # Mock property shape
        shape = PropertyShape(
            pid="P31",
            datatype="wikibase-item",
            predicates=PropertyPredicates(
                direct="wdt:P31",
                statement="ps:P31",
                qualifier="pq:P31",
                reference="pr:P31"
            )
        )

        # Mock property registry
        mock_registry = PropertyRegistry(properties={})

        with patch('models.rdf_builder.writers.triple.ValueFormatter.format_value', return_value="wd:Q5"):
            TripleWriters.write_statement(output, "Q42", rdf_statement, shape, mock_registry)

        result = output.getvalue()

        # Should not have any qualifier or reference triples
        assert "pq:" not in result
        assert "pqv:" not in result
        assert "prov:wasDerivedFrom" not in result
        assert "pr:" not in result

    def test_write_statement_multiple_qualifiers(self) -> None:
        """Test writing statement with multiple qualifiers."""
        output = io.StringIO()

        # Create multiple qualifiers
        qualifiers = []
        for i in range(3):
            qualifier = MagicMock()
            qualifier.value = f"value_{i}"
            qualifier.property = f"P{i+580}"
            qualifiers.append(qualifier)

        # Mock RDF statement
        rdf_statement = RDFStatement(
            guid="Q42$GUID123",
            property_id="P31",
            value="wd:Q5",
            rank="normal",
            qualifiers=qualifiers,
            references=[]
        )

        # Mock property shape
        shape = PropertyShape(
            pid="P31",
            datatype="wikibase-item",
            predicates=PropertyPredicates(
                direct="wdt:P31",
                statement="ps:P31",
                qualifier="pq:P31",
                reference="pr:P31"
            )
        )

        # Mock property registry
        mock_registry = PropertyRegistry(properties={})

        with patch('models.rdf_builder.writers.triple.ValueFormatter.format_value', return_value="wd:Q5"):
            TripleWriters.write_statement(output, "Q42", rdf_statement, shape, mock_registry)

        result = output.getvalue()

        # Should have qualifier triples for each qualifier
        for i in range(3):
            assert f"pq:P{i+580}" in result