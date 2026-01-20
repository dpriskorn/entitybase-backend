"""
Tests for EntityDiffWorker
"""

from unittest.mock import Mock

import pytest

from models.workers.entity_diff_worker import (
    EntityDiffWorker,
    EntityDiffRequest,
    EntityDiffResponse,
    RDFCanonicalizer,
    CanonicalizationMethod,
    diff_rdf_content,
)


class TestRDFCanonicalizer:
    """Test RDF canonicalization methods."""

    def test_urdna2015_canonicalization(self) -> None:
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

    def test_skolem_canonicalization(self) -> None:
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

    @pytest.mark.asyncio
    async def test_compute_diff_no_changes(self):
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
            format="turtle",
        )

        response = await self.worker.compute_diff(request)

        assert isinstance(response, EntityDiffResponse)
        assert response.entity_id == "Q42"
        assert len(response.added_triples) == 0
        assert len(response.removed_triples) == 0
        assert response.triple_count_v1 == response.triple_count_v2
        assert response.processing_time_ms >= 0

    @pytest.mark.asyncio
    async def test_compute_diff_with_changes(self):
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
            format="turtle",
        )

        response = await self.worker.compute_diff(request)

        assert isinstance(response, EntityDiffResponse)
        assert response.entity_id == "Q42"
        # Should have added triples (the birth date)
        assert len(response.added_triples) >= 1
        assert len(response.removed_triples) == 0
        assert response.triple_count_v2 > response.triple_count_v1


async def test_diff_rdf_content() -> None:
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

    result = await diff_rdf_content(rdf_v1, rdf_v2)

    assert "added" in result
    assert "removed" in result
    assert "canonicalization_method" in result
    assert "processing_time_ms" in result
    assert len(result["added"]) >= 1
    assert len(result["removed"]) == 0


class TestRDFStreaming:
    """Test RDF change event streaming."""

    def setup_method(self):
        """Set up test fixtures."""
        from models.infrastructure.stream.producer import StreamProducerClient

        self.mock_producer = Mock()
        self.rdf_producer = StreamProducerClient(
            bootstrap_servers="localhost:9092", topic="test.rdf.changes"
        )
        self.rdf_producer.producer = self.mock_producer

    def test_rdf_change_event_creation(self) -> None:
        """Test RDF change event model creation."""
        from models.rest_api.entitybase.v1.response.events import RDFChangeEvent

        event = RDFChangeEvent(
            meta={
                "dt": "2024-01-14T12:00:00Z",
                "stream": "wikibase.entity_diff",
                "id": "Q42-150",
                "domain": "wikibase.org",
                "uri": "https://www.wikidata.org/wiki/Q42",
            },
            entity_id="Q42",
            revision_id=150,
            from_revision_id=149,
            added_triples=[("wd:Q42", "wdt:P569", '"1952-03-11"^^xsd:dateTime')],
            removed_triples=[],
            canonicalization_method="urdna2015",
            triple_count_diff=1,
            title="Q42",
            user="system",
            timestamp=1705233600,
            comment="RDF diff: +1 -0 triples",
            revision={"new": 150, "old": 149},
            length={"new": 150, "old": 149},
            server_name="wikibase-backend",
            server_url="https://wikibase-backend.example.com",
            wiki="wikidatawiki",
            patrolled=False,
        )

        assert event.entity_id == "Q42"
        assert event.revision_id == 150
        assert len(event.added_triples) == 1
        assert len(event.removed_triples) == 0
        assert event.canonicalization_method == "urdna2015"
        assert event.triple_count_diff == 1

    async def test_publish_rdf_change(self):
        """Test publishing RDF change event."""
        from models.rest_api.entitybase.v1.response.events import RDFChangeEvent

        event = RDFChangeEvent(
            meta={
                "dt": "2024-01-14T12:00:00Z",
                "stream": "wikibase.entity_diff",
                "id": "Q42-150",
                "domain": "wikibase.org",
                "uri": "https://www.wikidata.org/wiki/Q42",
            },
            entity_id="Q42",
            revision_id=150,
            added_triples=[],
            removed_triples=[],
            canonicalization_method="urdna2015",
            triple_count_diff=0,
            title="Q42",
            user="system",
            timestamp=1705233600,
            comment="RDF diff: +0 -0 triples",
            revision={"new": 150, "old": 149},
            length={"new": 150, "old": 149},
            server_name="wikibase-backend",
            server_url="https://wikibase-backend.example.com",
            wiki="wikidatawiki",
            patrolled=False,
        )

        await self.rdf_producer.publish_change(event)

        self.mock_producer.send_and_wait.assert_called_once()
        call_args = self.mock_producer.send_and_wait.call_args
        assert call_args[1]["topic"] == "test.rdf.changes"
        assert call_args[1]["key"] == "Q42"

    async def test_entity_diff_worker_with_streaming(self):
        """Test EntityDiffWorker with RDF streaming enabled."""
        from models.workers.entity_diff_worker import (
            EntityDiffWorker,
            EntityDiffRequest,
        )

        worker = EntityDiffWorker(rdf_stream_producer=self.rdf_producer)

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
            format="turtle",
            from_revision_id=149,
        )

        response = await worker.compute_diff(request)

        assert response.entity_id == "Q42"
        assert len(response.added_triples) >= 1
        assert len(response.removed_triples) == 0

        # Verify event was published
        self.mock_producer.send_and_wait.assert_called_once()
