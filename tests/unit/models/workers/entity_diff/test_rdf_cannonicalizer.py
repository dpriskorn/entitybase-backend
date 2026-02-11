"""Unit tests for RDFCanonicalizer."""

import pytest

from pyld import jsonld
from rdflib import Graph, Literal, URIRef

from models.workers.entity_diff.rdf_cannonicalizer import RDFCanonicalizer
from models.workers.entity_diff.enums import CanonicalizationMethod


@pytest.mark.unit
class TestRDFCanonicalizerURDNA2015:
    """Tests for URDNA2015 canonicalization method."""

    def test_canonicalize_simple_turtle(self):
        """Test canonicalizing simple Turtle RDF."""
        rdf_content = """
        @prefix wd: <http://www.wikidata.org/entity/> .
        @prefix wdt: <http://www.wikidata.org/prop/direct/> .
        
        wd:Q42 wdt:P31 wd:Q5 .
        """

        canonicalizer = RDFCanonicalizer(method=CanonicalizationMethod.URDNA2015)
        triples = canonicalizer.canonicalize(rdf_content, format_="turtle")

        assert isinstance(triples, set)
        assert len(triples) > 0
        assert all(isinstance(triple, tuple) and len(triple) == 3 for triple in triples)

    def test_canonicalize_with_multiple_statements(self):
        """Test canonicalizing RDF with multiple statements."""
        rdf_content = """
        @prefix wd: <http://www.wikidata.org/entity/> .
        @prefix wdt: <http://www.wikidata.org/prop/direct/> .
        
        wd:Q42 wdt:P31 wd:Q5 .
        wd:Q42 wdt:P21 wd:Q6581072 .
        wd:Q42 wdt:P27 wd:Q30 .
        """

        canonicalizer = RDFCanonicalizer(method=CanonicalizationMethod.URDNA2015)
        triples = canonicalizer.canonicalize(rdf_content, format_="turtle")

        assert len(triples) == 3

    def test_canonicalize_with_literal(self):
        """Test canonicalizing RDF with literal values."""
        rdf_content = """
        @prefix wd: <http://www.wikidata.org/entity/> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        
        wd:Q42 rdfs:label "Douglas Adams"@en .
        """

        canonicalizer = RDFCanonicalizer(method=CanonicalizationMethod.URDNA2015)
        triples = canonicalizer.canonicalize(rdf_content, format_="turtle")

        assert len(triples) > 0

    def test_canonicalize_empty_rdf(self):
        """Test canonicalizing empty RDF."""
        rdf_content = ""

        canonicalizer = RDFCanonicalizer(method=CanonicalizationMethod.URDNA2015)
        triples = canonicalizer.canonicalize(rdf_content, format_="turtle")

        assert isinstance(triples, set)
        assert len(triples) == 0

    def test_canonicalize_with_blank_nodes(self):
        """Test canonicalizing RDF with blank nodes."""
        rdf_content = """
        @prefix wd: <http://www.wikidata.org/entity/> .
        @prefix wdt: <http://www.wikidata.org/prop/direct/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        wd:Q42 wdt:P569 [ wdt:P577 "1952-03-11"^^xsd:dateTime ] .
        """

        canonicalizer = RDFCanonicalizer(method=CanonicalizationMethod.URDNA2015)
        triples = canonicalizer.canonicalize(rdf_content, format_="turtle")

        assert len(triples) > 0


@pytest.mark.unit
class TestRDFCanonicalizerSkolem:
    """Tests for Skolemization canonicalization method."""

    def test_canonicalize_skolem_simple(self):
        """Test canonicalizing with skolemization."""
        rdf_content = """
        @prefix wd: <http://www.wikidata.org/entity/> .
        @prefix wdt: <http://www.wikidata.org/prop/direct/> .
        
        wd:Q42 wdt:P31 wd:Q5 .
        """

        canonicalizer = RDFCanonicalizer(method=CanonicalizationMethod.SKOLEM)
        triples = canonicalizer.canonicalize(rdf_content, format_="turtle")

        assert isinstance(triples, set)
        assert len(triples) > 0

    def test_canonicalize_skolem_with_blank_nodes(self):
        """Test skolemization with blank nodes."""
        rdf_content = """
        @prefix wd: <http://www.wikidata.org/entity/> .
        @prefix wdt: <http://www.wikidata.org/prop/direct/> .
        
        wd:Q42 wdt:P26 _:b1 .
        _:b1 wdt:P31 wd:Q5 .
        """

        canonicalizer = RDFCanonicalizer(method=CanonicalizationMethod.SKOLEM)
        triples = canonicalizer.canonicalize(rdf_content, format_="turtle")

        assert len(triples) > 0

    def test_canonicalize_skolem_empty(self):
        """Test skolemization with empty RDF."""
        rdf_content = ""

        canonicalizer = RDFCanonicalizer(method=CanonicalizationMethod.SKOLEM)
        triples = canonicalizer.canonicalize(rdf_content, format_="turtle")

        assert len(triples) == 0


@pytest.mark.unit
class TestRDFCanonicalizerStructuralHash:
    """Tests for structural hash canonicalization method."""

    def test_canonicalize_structural_hash_simple(self):
        """Test canonicalizing with structural hash."""
        rdf_content = """
        @prefix wd: <http://www.wikidata.org/entity/> .
        @prefix wdt: <http://www.wikidata.org/prop/direct/> .
        
        wd:Q42 wdt:P31 wd:Q5 .
        """

        canonicalizer = RDFCanonicalizer(method=CanonicalizationMethod.STRUCTURAL_HASH)
        triples = canonicalizer.canonicalize(rdf_content, format_="turtle")

        assert isinstance(triples, set)
        assert len(triples) > 0

    def test_canonicalize_structural_hash_normalizes_terms(self):
        """Test that structural hash normalizes RDF terms."""
        g = Graph()
        g.add(
            (
                URIRef("http://example.org/subject"),
                URIRef("http://example.org/predicate"),
                Literal("object"),
            )
        )

        rdf_content = g.serialize(format="turtle")

        canonicalizer = RDFCanonicalizer(method=CanonicalizationMethod.STRUCTURAL_HASH)
        triples = canonicalizer.canonicalize(rdf_content, format_="turtle")

        assert len(triples) > 0
        assert all(isinstance(triple, tuple) for triple in triples)

    def test_canonicalize_structural_hash_empty(self):
        """Test structural hash with empty RDF."""
        rdf_content = ""

        canonicalizer = RDFCanonicalizer(method=CanonicalizationMethod.STRUCTURAL_HASH)
        triples = canonicalizer.canonicalize(rdf_content, format_="turtle")

        assert len(triples) == 0

    def test_canonicalize_structural_hash_ignores_bnode_ids(self):
        """Test that structural hash ignores blank node IDs."""
        rdf_content = """
        @prefix wd: <http://www.wikidata.org/entity/> .
        @prefix wdt: <http://www.wikidata.org/prop/direct/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        wd:Q42 wdt:P569 [ wdt:P577 "1952-03-11"^^xsd:dateTime ] .
        wd:Q42 wdt:P569 [ wdt:P577 "1952-03-11"^^xsd:dateTime ] .
        """

        canonicalizer = RDFCanonicalizer(method=CanonicalizationMethod.STRUCTURAL_HASH)
        triples = canonicalizer.canonicalize(rdf_content, format_="turtle")

        assert len(triples) > 0


@pytest.mark.unit
class TestRDFCanonicalizerDefault:
    """Tests for default behavior and edge cases."""

    def test_default_method_is_urdna2015(self):
        """Test that URDNA2015 is the default method."""
        canonicalizer = RDFCanonicalizer()
        assert canonicalizer.method == CanonicalizationMethod.URDNA2015

    def test_unsupported_method_raises_error(self):
        """Test that unsupported canonicalization method raises validation error."""
        from pydantic import ValidationError

        rdf_content = "@prefix wd: <http://www.wikidata.org/entity/> ."

        with pytest.raises(ValidationError, match="Input should be"):
            RDFCanonicalizer(method="unsupported_method")

    def test_extract_triples_from_nquads_with_comments(self):
        """Test extracting triples from N-Quads with comments."""
        nquads = """# This is a comment
        <http://example.org/s> <http://example.org/p> <http://example.org/o> .
        # Another comment
        <http://example.org/s2> <http://example.org/p2> <http://example.org/o2> .
        """

        canonicalizer = RDFCanonicalizer()
        triples = canonicalizer._extract_triples_from_nquads(nquads)

        assert len(triples) == 2

    def test_extract_triples_from_nquads_with_graph(self):
        """Test extracting triples from N-Quads with graph component."""
        nquads = "<http://example.org/s> <http://example.org/p> <http://example.org/o> <http://example.org/g> ."

        canonicalizer = RDFCanonicalizer()
        triples = canonicalizer._extract_triples_from_nquads(nquads)

        assert len(triples) == 1

    def test_extract_triples_from_nquads_with_multi_word_object(self):
        """Test extracting triples with multi-word object."""
        nquads = '<http://example.org/s> <http://example.org/p> "multi word object" .'

        canonicalizer = RDFCanonicalizer()
        triples = canonicalizer._extract_triples_from_nquads(nquads)

        assert len(triples) == 1
        assert any("multi word object" in str(triple[2]) for triple in triples)

    def test_normalize_term_with_n3_method(self):
        """Test normalizing terms with n3() method."""
        g = Graph()
        uri = URIRef("http://example.org/test")

        canonicalizer = RDFCanonicalizer()
        normalized = canonicalizer._normalize_term(uri)

        assert isinstance(normalized, str)

    def test_normalize_term_without_n3_method(self):
        """Test normalizing terms without n3() method."""
        canonicalizer = RDFCanonicalizer()
        normalized = canonicalizer._normalize_term("plain_string")

        assert normalized == "plain_string"
