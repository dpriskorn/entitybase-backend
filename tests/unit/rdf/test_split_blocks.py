def split_subject_blocks(ttl: str) -> dict[str, str]:
    blocks = {}
    current_subject = None
    current_lines = []

    for line in ttl.splitlines():
        if not line.strip():
            continue

        line_stripped = line.strip()
        if line_stripped.lower().startswith("@prefix"):
            continue

        if line_stripped.startswith("<http") or line_stripped.startswith("<https"):
            continue

        if line and not line.startswith((" ", "\t")):
            if current_subject:
                blocks[current_subject] = "\n".join(current_lines).strip()
            current_subject = list(line.split())[0]
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_subject:
        blocks[current_subject] = "\n".join(current_lines).strip()

    return blocks


def test_split_blocks_skips_prefixes() -> None:
    """Test that @prefix lines are skipped"""
    input_ttl = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
wd:Q42 a schema:Thing ."""

    blocks = split_subject_blocks(input_ttl)

    assert "@prefix" not in blocks
    assert "wd:Q42" in blocks


def test_split_blocks_includes_all_subjects() -> None:
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


def test_split_blocks_preserves_predicates() -> None:
    """Test that predicate blocks are preserved"""
    input_ttl = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
wd:Q42 a schema:Thing ;
	rdfs:label "Test"@en ;
	schema:description "A test"@en ."""

    blocks = split_subject_blocks(input_ttl)

    assert "rdfs:label" in blocks["wd:Q42"]
    assert "schema:description" in blocks["wd:Q42"]


def test_split_blocks_empty_input() -> None:
    """Test that empty input is handled correctly"""
    blocks = split_subject_blocks("")
    assert len(blocks) == 0
