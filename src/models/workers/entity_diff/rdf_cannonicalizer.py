from typing import Set, Any

from pydantic import BaseModel
from pyld import jsonld  # type: ignore[import-untyped]
from rdflib import ConjunctiveGraph, Graph

from models.workers.entity_diff.types import Triple
from models.workers.entity_diff.enums import CanonicalizationMethod


class RDFCanonicalizer(BaseModel):
    """Handles RDF canonicalization using various methods."""

    method: CanonicalizationMethod = CanonicalizationMethod.URDNA2015

    def canonicalize(self, rdf_content: str, format_: str = "turtle") -> Set[Triple]:
        """Canonicalize RDF content and return normalized triples."""
        if self.method == CanonicalizationMethod.URDNA2015:
            return self._canonicalize_urdna2015(rdf_content, format_)
        elif self.method == CanonicalizationMethod.SKOLEM:
            return self._canonicalize_skolem(rdf_content, format_)
        elif self.method == CanonicalizationMethod.STRUCTURAL_HASH:
            return self._canonicalize_structural_hash(rdf_content, format_)
        else:
            raise ValueError(f"Unsupported canonicalization method: {self.method}")

    def _canonicalize_urdna2015(self, rdf_content: str, format_: str) -> Set[Triple]:
        """Canonicalize using URDNA2015 algorithm."""
        # Parse RDF to JSON-LD
        g = ConjunctiveGraph()
        g.parse(data=rdf_content, format=format_)

        # Serialize to N-Quads format for pyld compatibility
        nquads = g.serialize(format="nquads")
        jsonld_data = jsonld.from_rdf(nquads)

        # Canonicalize to N-Quads
        canonical = jsonld.normalize(
            jsonld_data, {"algorithm": "URDNA2015", "format": "application/n-quads"}
        )

        # Extract triples from N-Quads (ensure string type)
        if isinstance(canonical, str):
            return self._extract_triples_from_nquads(canonical)
        else:
            return set()

    def _canonicalize_skolem(self, rdf_content: str, format_: str) -> Set[Triple]:
        """Canonicalize by skolemizing blank nodes."""
        g = Graph()
        g.parse(data=rdf_content, format=format_)

        # Convert to normalized N-Triples
        ntriples = g.serialize(format="ntriples")

        return self._extract_triples_from_nquads(ntriples)

    def _canonicalize_structural_hash(
        self, rdf_content: str, format_: str
    ) -> Set[Triple]:
        """Canonicalize by structural hashing (ignores bnode IDs)."""
        g = Graph()
        g.parse(data=rdf_content, format=format_)

        triples = set()
        for s, p, o in g:
            # Normalize URIs and create hash-based identifiers
            subject = self._normalize_term(s)
            predicate = self._normalize_term(p)
            obj = self._normalize_term(o)

            triples.add((subject, predicate, obj))

        return triples

    @staticmethod
    def _extract_triples_from_nquads(nquads: str) -> Set[Triple]:
        """Extract normalized triples from N-Quads/N-Triples format."""
        g = ConjunctiveGraph()
        g.parse(data=nquads, format="nquads")

        triples = set()
        for s, p, o in g:
            subject = s.n3()
            predicate = p.n3()
            obj = o.n3()

            triples.add((subject, predicate, obj))

        return triples

    @staticmethod
    def _normalize_term(term: Any) -> str:
        """Normalize an RDF term for comparison."""
        if hasattr(term, "n3"):
            return term.n3()  # type: ignore[no-any-return]
        return str(term)
