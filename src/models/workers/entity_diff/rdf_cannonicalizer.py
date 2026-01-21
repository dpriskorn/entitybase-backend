from typing import Set, Any

from pydantic import BaseModel
from pyld import jsonld
from rdflib import Graph

from models.workers.entity_diff.entity_diff_worker import Triple
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
        g = Graph()
        g.parse(data=rdf_content, format=format_)
        jsonld_data = jsonld.from_rdf(g)

        # Canonicalize to N-Quads
        canonical = jsonld.normalize(
            jsonld_data, {"algorithm": "URDNA2015", "format": "application/n-quads"}
        )

        # Extract triples from N-Quads
        return self._extract_triples_from_nquads(canonical)

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
        triples = set()

        for line in nquads.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Parse N-Quad/N-Triple: subject predicate object [graph] .
            parts = line.rstrip(" .").split()
            if len(parts) >= 3:
                subject = parts[0]
                predicate = parts[1]
                obj = " ".join(parts[2:-1]) if len(parts) > 3 else parts[2]
                # Ignore graph part if present

                triples.add((subject, predicate, obj))

        return triples

    @staticmethod
    def _normalize_term(term: Any) -> str:
        """Normalize an RDF term for comparison."""
        if hasattr(term, "n3"):
            return term.n3()  # type: ignore[no-any-return]
        return str(term)
