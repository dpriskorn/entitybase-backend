#!/usr/bin/env python3
"""
test_canonicalization.py - Prototype RDF canonicalization and diffing for entity versions
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import RDF, RDFS
from pyld import jsonld
import json
import hashlib


def parse_rdf_to_jsonld(rdf_content: str, format: str = "turtle") -> dict:
    """Parse RDF content to JSON-LD format for canonicalization."""
    g = Graph()
    g.parse(data=rdf_content, format=format)

    # Convert to JSON-LD
    jsonld_data = jsonld.from_rdf(g)

    return jsonld_data


def canonicalize_jsonld(jsonld_data: dict) -> str:
    """Canonicalize JSON-LD using URDNA2015 algorithm."""
    canonical = jsonld.normalize(jsonld_data, {'algorithm': 'URDNA2015', 'format': 'application/n-quads'})
    return canonical


def extract_triples_from_nquads(nquads: str) -> set[tuple]:
    """Extract normalized triples from N-Quads format."""
    triples = set()

    for line in nquads.strip().split('\n'):
        if line.strip():
            # Parse N-Quad: subject predicate object graph .
            parts = line.strip().split()
            if len(parts) >= 4:
                subject = parts[0]
                predicate = parts[1]
                obj = parts[2]
                # Ignore graph part for now

                # Create normalized tuple
                triple = (subject, predicate, obj)
                triples.add(triple)

    return triples


def compute_diff(triples_a: set, triples_b: set) -> dict:
    """Compute set difference between two triple sets."""
    return {
        "added": triples_b - triples_a,
        "removed": triples_a - triples_b
    }


def test_canonicalization():
    """Test canonicalization with sample RDF data."""

    # Sample RDF content for an entity (simplified Wikibase-style)
    rdf_v1 = """
    @prefix wd: <http://www.wikidata.org/entity/> .
    @prefix wdt: <http://www.wikidata.org/prop/direct/> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

    wd:Q42 wdt:P31 wd:Q5 ;
          rdfs:label "Douglas Adams"@en .
    """

    rdf_v2 = """
    @prefix wd: <http://www.wikidata.org/entity/> .
    @prefix wdt: <http://www.wikidata.org/prop/direct/> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

    wd:Q42 wdt:P31 wd:Q5 ;
          rdfs:label "Douglas Adams"@en ;
          wdt:P569 "1952-03-11"^^<http://www.w3.org/2001/XMLSchema#dateTime> .
    """

    print("=== Testing RDF Canonicalization ===\n")

    try:
        # Canonicalize version 1
        print("Canonicalizing RDF v1...")
        jsonld_v1 = parse_rdf_to_jsonld(rdf_v1, "turtle")
        canonical_v1 = canonicalize_jsonld(jsonld_v1)
        triples_v1 = extract_triples_from_nquads(canonical_v1)

        print(f"V1 canonical triples: {len(triples_v1)}")
        for triple in sorted(triples_v1):
            print(f"  {triple}")

        # Canonicalize version 2
        print("\nCanonicalizing RDF v2...")
        jsonld_v2 = parse_rdf_to_jsonld(rdf_v2, "turtle")
        canonical_v2 = canonicalize_jsonld(jsonld_v2)
        triples_v2 = extract_triples_from_nquads(canonical_v2)

        print(f"V2 canonical triples: {len(triples_v2)}")
        for triple in sorted(triples_v2):
            print(f"  {triple}")

        # Compute diff
        print("\n=== Computing Diff ===")
        diff = compute_diff(triples_v1, triples_v2)

        print(f"Added triples ({len(diff['added'])}):")
        for triple in sorted(diff['added']):
            print(f"  + {triple}")

        print(f"\nRemoved triples ({len(diff['removed'])}):")
        for triple in sorted(diff['removed']):
            print(f"  - {triple}")

        print("\n=== Test Completed Successfully ===")

    except Exception as e:
        print(f"Error during canonicalization test: {e}")
        import traceback
        traceback.print_exc()


def test_blank_nodes():
    """Test canonicalization with blank nodes."""
    print("\n=== Testing Blank Nodes ===\n")

    rdf_with_bnodes = """
    @prefix wd: <http://www.wikidata.org/entity/> .
    @prefix wdt: <http://www.wikidata.org/prop/direct/> .

    wd:Q42 wdt:P31 wd:Q5 ;
          wdt:P39 _:statement1 .

    _:statement1 wdt:P39 wd:Q5 .
    """

    try:
        jsonld_data = parse_rdf_to_jsonld(rdf_with_bnodes, "turtle")
        canonical = canonicalize_jsonld(jsonld_data)
        triples = extract_triples_from_nquads(canonical)

        print(f"Triples with canonicalized blank nodes: {len(triples)}")
        for triple in sorted(triples):
            print(f"  {triple}")

    except Exception as e:
        print(f"Error testing blank nodes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_canonicalization()
    test_blank_nodes()