#!/usr/bin/env python3
"""Test script to verify the fix for the multi-word object issue."""

from models.workers.entity_diff.rdf_cannonicalizer import RDFCanonicalizer

# Test case 1: Multi-word literal (the failing test)
nquads1 = '<http://example.org/s> <http://example.org/p> "multi word object" .'
canonicalizer = RDFCanonicalizer()
triples1 = canonicalizer._extract_triples_from_nquads(nquads1)

print("Test 1: Multi-word literal")
print(f"Input: {nquads1}")
print(f"Number of triples: {len(triples1)}")
for i, triple in enumerate(triples1):
    print(f"  Triple {i}: {triple}")
    has_multi_word = "multi word object" in str(triple[2])
    print(f"  'multi word object' in object: {has_multi_word}")

if len(triples1) == 1 and any("multi word object" in str(triple[2]) for triple in triples1):
    print("✓ Test 1 PASSED")
else:
    print("✗ Test 1 FAILED")

print()

# Test case 2: Comments (should still work)
nquads2 = """# This is a comment
<http://example.org/s> <http://example.org/p> <http://example.org/o> .
# Another comment
<http://example.org/s2> <http://example.org/p2> <http://example.org/o2> .
"""
triples2 = canonicalizer._extract_triples_from_nquads(nquads2)

print("Test 2: N-Quads with comments")
print(f"Number of triples: {len(triples2)}")
if len(triples2) == 2:
    print("✓ Test 2 PASSED")
else:
    print("✗ Test 2 FAILED")

print()

# Test case 3: Graph component (should still work)
nquads3 = "<http://example.org/s> <http://example.org/p> <http://example.org/o> <http://example.org/g> ."
triples3 = canonicalizer._extract_triples_from_nquads(nquads3)

print("Test 3: N-Quads with graph component")
print(f"Number of triples: {len(triples3)}")
if len(triples3) == 1:
    print("✓ Test 3 PASSED")
else:
    print("✗ Test 3 FAILED")

print()

# Test case 4: Language-tagged literal
nquads4 = '<http://example.org/s> <http://example.org/p> "label"@en .'
triples4 = canonicalizer._extract_triples_from_nquads(nquads4)

print("Test 4: Language-tagged literal")
print(f"Number of triples: {len(triples4)}")
for i, triple in enumerate(triples4):
    print(f"  Triple {i}: {triple}")
if len(triples4) == 1 and any('"label"@en' in str(triple[2]) for triple in triples4):
    print("✓ Test 4 PASSED")
else:
    print("✗ Test 4 FAILED")
