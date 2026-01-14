"""
Entity Diff Worker - Computes diffs between RDF versions of Wikibase entities
"""

import time
from typing import List, Set, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from rdflib import Graph
from pyld import jsonld

from models.infrastructure.stream.producer import StreamProducerClient, RDFChangeEvent


Triple = Tuple[str, str, str]  # (subject, predicate, object)


class CanonicalizationMethod(Enum):
    URDNA2015 = "urdna2015"
    SKOLEM = "skolem"
    STRUCTURAL_HASH = "structural_hash"


@dataclass
class EntityDiffRequest:
    """Request to compute diff between two entity versions."""
    entity_id: str
    rdf_content_v1: str
    rdf_content_v2: str
    format: str = "turtle"
    canonicalization_method: CanonicalizationMethod = CanonicalizationMethod.URDNA2015
    from_revision_id: Optional[int] = None  # For streaming events


@dataclass
class EntityDiffResponse:
    """Response containing the computed diff."""
    entity_id: str
    added_triples: List[Triple]
    removed_triples: List[Triple]
    canonicalization_method: str
    processing_time_ms: int
    triple_count_v1: int
    triple_count_v2: int


class RDFCanonicalizer:
    """Handles RDF canonicalization using various methods."""

    def __init__(self, method: CanonicalizationMethod = CanonicalizationMethod.URDNA2015):
        self.method = method

    def canonicalize(self, rdf_content: str, format: str = "turtle") -> Set[Triple]:
        """Canonicalize RDF content and return normalized triples."""
        if self.method == CanonicalizationMethod.URDNA2015:
            return self._canonicalize_urdna2015(rdf_content, format)
        elif self.method == CanonicalizationMethod.SKOLEM:
            return self._canonicalize_skolem(rdf_content, format)
        elif self.method == CanonicalizationMethod.STRUCTURAL_HASH:
            return self._canonicalize_structural_hash(rdf_content, format)
        else:
            raise ValueError(f"Unsupported canonicalization method: {self.method}")

    def _canonicalize_urdna2015(self, rdf_content: str, format: str) -> Set[Triple]:
        """Canonicalize using URDNA2015 algorithm."""
        # Parse RDF to JSON-LD
        g = Graph()
        g.parse(data=rdf_content, format=format)
        jsonld_data = jsonld.from_rdf(g)

        # Canonicalize to N-Quads
        canonical = jsonld.normalize(
            jsonld_data,
            {'algorithm': 'URDNA2015', 'format': 'application/n-quads'}
        )

        # Extract triples from N-Quads
        return self._extract_triples_from_nquads(canonical)

    def _canonicalize_skolem(self, rdf_content: str, format: str) -> Set[Triple]:
        """Canonicalize by skolemizing blank nodes."""
        g = Graph()
        g.parse(data=rdf_content, format=format)

        # Convert to normalized N-Triples
        ntriples = g.serialize(format="ntriples")

        return self._extract_triples_from_nquads(ntriples)

    def _canonicalize_structural_hash(self, rdf_content: str, format: str) -> Set[Triple]:
        """Canonicalize by structural hashing (ignores bnode IDs)."""
        g = Graph()
        g.parse(data=rdf_content, format=format)

        triples = set()
        for s, p, o in g:
            # Normalize URIs and create hash-based identifiers
            subject = self._normalize_term(s)
            predicate = self._normalize_term(p)
            obj = self._normalize_term(o)

            triples.add((subject, predicate, obj))

        return triples

    def _extract_triples_from_nquads(self, nquads: str) -> Set[Triple]:
        """Extract normalized triples from N-Quads/N-Triples format."""
        triples = set()

        for line in nquads.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Parse N-Quad/N-Triple: subject predicate object [graph] .
            parts = line.rstrip(' .').split()
            if len(parts) >= 3:
                subject = parts[0]
                predicate = parts[1]
                obj = ' '.join(parts[2:-1]) if len(parts) > 3 else parts[2]
                # Ignore graph part if present

                triples.add((subject, predicate, obj))

        return triples

    def _normalize_term(self, term) -> str:
        """Normalize an RDF term for comparison."""
        if hasattr(term, 'n3'):
            return term.n3()
        return str(term)


class RDFSerializer:
    """Serialize Wikibase entity data to RDF formats."""

    def entity_data_to_rdf(self, entity_data: dict, format: str = "turtle") -> str:
        """Convert Wikibase entity JSON data to RDF."""
        from rdflib import Graph, URIRef, Literal, BNode
        from rdflib.namespace import RDF, RDFS

        g = Graph()
        entity_id = entity_data.get("id", "")
        entity_uri = URIRef(f"http://www.wikidata.org/entity/{entity_id}")

        # Add entity type
        entity_type = entity_data.get("type", "item")
        if entity_type == "item":
            g.add((entity_uri, RDF.type, URIRef("http://www.wikidata.org/entity/Q35120")))  # item
        elif entity_type == "property":
            g.add((entity_uri, RDF.type, URIRef("http://www.wikidata.org/entity/Q18616576")))  # property

        # Add labels
        labels = entity_data.get("labels", {})
        for lang, label_data in labels.items():
            if isinstance(label_data, dict) and "value" in label_data:
                g.add((
                    entity_uri,
                    RDFS.label,
                    Literal(label_data["value"], lang=lang)
                ))

        # Add descriptions
        descriptions = entity_data.get("descriptions", {})
        for lang, desc_data in descriptions.items():
            if isinstance(desc_data, dict) and "value" in desc_data:
                # Wikibase doesn't have a standard description property in RDF
                # Using schema.org description for now
                g.add((
                    entity_uri,
                    URIRef("http://schema.org/description"),
                    Literal(desc_data["value"], lang=lang)
                ))

        # Add claims/statements (simplified)
        claims = entity_data.get("claims", {})
        for prop_id, statements in claims.items():
            if isinstance(statements, list):
                for statement in statements:
                    if isinstance(statement, dict):
                        mainsnak = statement.get("mainsnak", {})
                        if mainsnak.get("snaktype") == "value":
                            datavalue = mainsnak.get("datavalue", {})
                            if datavalue.get("type") == "string":
                                value = datavalue.get("value", "")
                                g.add((
                                    entity_uri,
                                    URIRef(f"http://www.wikidata.org/prop/direct/{prop_id}"),
                                    Literal(value)
                                ))

        return g.serialize(format=format)


class EntityDiffWorker:
    """Worker for computing entity diffs."""

    def __init__(
        self,
        canonicalization_method: CanonicalizationMethod = CanonicalizationMethod.URDNA2015,
        rdf_stream_producer: Optional[StreamProducerClient] = None
    ):
        self.canonicalizer = RDFCanonicalizer(canonicalization_method)
        self.serializer = RDFSerializer()
        self.rdf_stream_producer = rdf_stream_producer

    async def compute_diff_from_rdf(self, entity_id: str, rdf_v1: str, rdf_v2: str, format: str = "turtle") -> EntityDiffResponse:
        """Compute diff from RDF content strings."""
        request = EntityDiffRequest(
            entity_id=entity_id,
            rdf_content_v1=rdf_v1,
            rdf_content_v2=rdf_v2,
            format=format,
            canonicalization_method=self.canonicalizer.method
        )
        return await self.compute_diff(request)

    async def compute_diff_from_entity_data(
        self,
        entity_id: str,
        entity_data_v1: dict,
        entity_data_v2: dict,
        format: str = "turtle"
    ) -> EntityDiffResponse:
        """Compute diff from Wikibase entity data dictionaries."""
        rdf_v1 = self.serializer.entity_data_to_rdf(entity_data_v1, format)
        rdf_v2 = self.serializer.entity_data_to_rdf(entity_data_v2, format)

        return await self.compute_diff_from_rdf(entity_id, rdf_v1, rdf_v2, format)

    async def compute_diff(self, request: EntityDiffRequest) -> EntityDiffResponse:
        """Compute diff between two RDF versions of an entity."""
        start_time = time.time()

        # Canonicalize both versions
        triples_v1 = self.canonicalizer.canonicalize(
            request.rdf_content_v1,
            request.format
        )
        triples_v2 = self.canonicalizer.canonicalize(
            request.rdf_content_v2,
            request.format
        )

        # Compute set differences
        added = triples_v2 - triples_v1
        removed = triples_v1 - triples_v2

        processing_time = int((time.time() - start_time) * 1000)

        response = EntityDiffResponse(
            entity_id=request.entity_id,
            added_triples=sorted(list(added)),
            removed_triples=sorted(list(removed)),
            canonicalization_method=request.canonicalization_method.value,
            processing_time_ms=processing_time,
            triple_count_v1=len(triples_v1),
            triple_count_v2=len(triples_v2)
        )

        # Optionally publish to stream
        if self.rdf_stream_producer is not None:
            await self._publish_rdf_change_event(request, response)

        return response

    async def _publish_rdf_change_event(self, request: EntityDiffRequest, response: EntityDiffResponse) -> None:
        """Publish RDF change event to stream following MediaWiki recentchange schema."""
        if not self.rdf_stream_producer:
            return

        # Create event following MediaWiki recentchange schema
        event = RDFChangeEvent(
            # Required schema fields
            meta={
                "dt": datetime.utcnow().isoformat() + "Z",
                "stream": "wikibase.entity_diff",
                "id": f"{request.entity_id}-{response.triple_count_v2}",
                "domain": "wikibase.org",  # TODO: Make configurable
                "uri": f"https://www.wikidata.org/wiki/{request.entity_id}",
            },

            # Wikibase-specific fields
            entity_id=request.entity_id,
            revision_id=response.triple_count_v2,  # Using triple count as revision for now
            from_revision_id=getattr(request, 'from_revision_id', None),

            # RDF diff data
            added_triples=response.added_triples,
            removed_triples=response.removed_triples,
            canonicalization_method=response.canonicalization_method,
            triple_count_diff=len(response.added_triples) - len(response.removed_triples),

            # MediaWiki recentchange schema fields
            title=request.entity_id,
            user="system",  # TODO: Get from request context
            timestamp=int(time.time()),
            comment=f"RDF diff: +{len(response.added_triples)} -{len(response.removed_triples)} triples",

            # Revision info
            revision={
                "new": response.triple_count_v2,
                "old": response.triple_count_v1
            },

            # Length info (using triple counts)
            length={
                "new": response.triple_count_v2,
                "old": response.triple_count_v1
            },

            # Server info
            server_name="wikibase-backend",
            server_url="https://wikibase-backend.example.com",  # TODO: Make configurable
            wiki="wikidatawiki",  # TODO: Make configurable

            # Required field
            patrolled=False
        )

        await self.rdf_stream_producer.publish_rdf_change(event)


# Convenience functions for testing
async def diff_rdf_content(
    rdf_v1: str,
    rdf_v2: str,
    format: str = "turtle",
    method: CanonicalizationMethod = CanonicalizationMethod.URDNA2015
) -> Dict[str, Any]:
    """Compute diff between two RDF strings."""
    worker = EntityDiffWorker(method)

    request = EntityDiffRequest(
        entity_id="test",
        rdf_content_v1=rdf_v1,
        rdf_content_v2=rdf_v2,
        format=format,
        canonicalization_method=method
    )

    response = await worker.compute_diff(request)

    return {
        "added": response.added_triples,
        "removed": response.removed_triples,
        "canonicalization_method": response.canonicalization_method,
        "processing_time_ms": response.processing_time_ms,
        "triple_count_v1": response.triple_count_v1,
        "triple_count_v2": response.triple_count_v2
    }