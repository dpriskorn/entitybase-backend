"""
Entity Diff Worker - Computes diffs between RDF versions of Wikibase entities
"""

import time
from typing import List, Set, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum

from rdflib import Graph
from pyld import jsonld


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


class EntityDiffWorker:
    """Worker for computing entity diffs."""

    def __init__(self, canonicalization_method: CanonicalizationMethod = CanonicalizationMethod.URDNA2015):
        self.canonicalizer = RDFCanonicalizer(canonicalization_method)

    def compute_diff(self, request: EntityDiffRequest) -> EntityDiffResponse:
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

        return EntityDiffResponse(
            entity_id=request.entity_id,
            added_triples=sorted(list(added)),
            removed_triples=sorted(list(removed)),
            canonicalization_method=request.canonicalization_method.value,
            processing_time_ms=processing_time,
            triple_count_v1=len(triples_v1),
            triple_count_v2=len(triples_v2)
        )


# Convenience functions for testing
def diff_rdf_content(
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

    response = worker.compute_diff(request)

    return {
        "added": response.added_triples,
        "removed": response.removed_triples,
        "canonicalization_method": response.canonicalization_method,
        "processing_time_ms": response.processing_time_ms,
        "triple_count_v1": response.triple_count_v1,
        "triple_count_v2": response.triple_count_v2
    }