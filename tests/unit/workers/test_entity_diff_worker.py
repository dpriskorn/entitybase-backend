"""
Tests for EntityDiffWorker
"""

import pytest
from models.workers.entity_diff_worker import (
    EntityDiffWorker,
    EntityDiffRequest,
    EntityDiffResponse,
    RDFCanonicalizer,
    CanonicalizationMethod,
    diff_rdf_content
)


class TestRDFCanonicalizer:
    """Test RDF canonicalization methods."""

    def test_urdna2015_canonicalization(self):
        """Test URDNA2015 canonicalization with simple RDF."""
        canonicalizer = RDFCanonicalizer(CanonicalizationMethod.URDNA2015)

        rdf_content = """
        @prefix wd: <http://www.wikidata.org/entity/> .
        @prefix wdt: <http://www.wikidata.org/prop/direct/> .

        wd:Q42 wdt:P31 wd:Q5 .
        """

        triples = canonicalizer.canonicalize(rdf_content, "turtle")

        # Should produce normalized triples
        assert isinstance(triples, set)
        assert len(triples) > 0

        # Check that triples are tuples
        for triple in triples:
            assert isinstance(triple, tuple)
            assert len(triple) == 3

    def test_skolem_canonicalization(self):
        """Test skolemization canonicalization."""
        canonicalizer = RDFCanonicalizer(CanonicalizationMethod.SKOLEM)

        rdf_content = """
        @prefix wd: <http://www.wikidata.org/entity/> .
        @prefix wdt: <http://www.wikidata.org/prop/direct/> .

        wd:Q42 wdt:P31 wd:Q5 .
        """

        triples = canonicalizer.canonicalize(rdf_content, "turtle")

        assert isinstance(triples, set)
        assert len(triples) > 0


class TestEntityDiffWorker:
    """Test the EntityDiffWorker."""

    def setup_method(self):
        """Set up test fixtures."""
        self.worker = EntityDiffWorker()

    def test_compute_diff_no_changes(self):
        """Test diff when both versions are identical."""
        rdf_content = """
        @prefix wd: <http://www.wikidata.org/entity/> .
        @prefix wdt: <http://www.wikidata.org/prop/direct/> .

        wd:Q42 wdt:P31 wd:Q5 .
        """

        request = EntityDiffRequest(
            entity_id="Q42",
            rdf_content_v1=rdf_content,
            rdf_content_v2=rdf_content,
            format="turtle"
        )

        response = self.worker.compute_diff(request)

        assert isinstance(response, EntityDiffResponse)
        assert response.entity_id == "Q42"
        assert len(response.added_triples) == 0
        assert len(response.removed_triples) == 0
        assert response.triple_count_v1 == response.triple_count_v2
        assert response.processing_time_ms >= 0

    def test_compute_diff_with_changes(self):
        """Test diff when versions have differences."""
        rdf_v1 = """
        @prefix wd: <http://www.wikidata.org/entity/> .
        @prefix wdt: <http://www.wikidata.org/prop/direct/> .

        wd:Q42 wdt:P31 wd:Q5 .
        """

        rdf_v2 = """
        @prefix wd: <http://www.wikidata.org/entity/> .
        @prefix wdt: <http://www.wikidata.org/prop/direct/> .

        wd:Q42 wdt:P31 wd:Q5 ;
              wdt:P569 "1952-03-11"^^<http://www.w3.org/2001/XMLSchema#dateTime> .
        """

        request = EntityDiffRequest(
            entity_id="Q42",
            rdf_content_v1=rdf_v1,
            rdf_content_v2=rdf_v2,
            format="turtle"
        )

        response = self.worker.compute_diff(request)

        assert isinstance(response, EntityDiffResponse)
        assert response.entity_id == "Q42"
        # Should have added triples (the birth date)
        assert len(response.added_triples) >= 1
        assert len(response.removed_triples) == 0
        assert response.triple_count_v2 > response.triple_count_v1


def test_diff_rdf_content():
    """Test the convenience function."""
    rdf_v1 = """
    @prefix wd: <http://www.wikidata.org/entity/> .
    @prefix wdt: <http://www.wikidata.org/prop/direct/> .

    wd:Q42 wdt:P31 wd:Q5 .
    """

    rdf_v2 = """
    @prefix wd: <http://www.wikidata.org/entity/> .
    @prefix wdt: <http://www.wikidata.org/prop/direct/> .

    wd:Q42 wdt:P31 wd:Q5 ;
          wdt:P21 wd:Q6581097 .  # Added gender
    """

    result = diff_rdf_content(rdf_v1, rdf_v2)

    assert "added" in result
    assert "removed" in result
    assert "canonicalization_method" in result
    assert "processing_time_ms" in result
    assert len(result["added"]) >= 1
    assert len(result["removed"]) == 0