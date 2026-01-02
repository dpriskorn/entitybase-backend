from rdf.conftest import split_subject_blocks


def test_split_blocks_skips_prefixes():
    """Test that @prefix lines are skipped"""
    input_ttl = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
wd:Q42 a schema:Thing ."""

    blocks = split_subject_blocks(input_ttl)

    assert "@prefix" not in blocks
    assert "wd:Q42" in blocks


def test_split_blocks_includes_all_subjects():
    """Test that all subjects are captured"""
    input_ttl = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
wd:Q42 a schema:Thing .
wd:Q43 a schema:Thing .
wd:Q44 a schema:Thing ."""

    blocks = split_subject_blocks(input_ttl)

    assert len(blocks) == 3
    assert "wd:Q42" in blocks
    assert "wd:Q43" in blocks
    assert "wd:Q44" in blocks


def test_split_blocks_preserves_predicates():
    """Test that predicate blocks are preserved"""
    input_ttl = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
wd:Q42 a schema:Thing ;
	rdfs:label "Test"@en ;
	schema:description "A test"@en ."""

    blocks = split_subject_blocks(input_ttl)

    assert "rdfs:label" in blocks["wd:Q42"]
    assert "schema:description" in blocks["wd:Q42"]


def test_split_blocks_empty_input():
    """Test that empty input is handled correctly"""
    blocks = split_subject_blocks("")
    assert len(blocks) == 0
