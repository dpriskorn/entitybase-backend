import json
from pathlib import Path

from .conftest import load_text, normalize_ttl, split_subject_blocks

# adjust import to your project
from wikibase_backend.rdf.export import entity_to_ttl


BASE = Path(__file__).parent
JSON_DIR = BASE / "test_data" / "json"
TTL_DIR = BASE / "test_data" / "ttl"


def test_Q120248304_matches_golden_ttl():
    """
    Full entity → TTL comparison against Wikidata golden output.
    """

    entity_id = "Q120248304"

    json_path = JSON_DIR / f"{entity_id}.json"
    ttl_path = TTL_DIR / f"{entity_id}.ttl"

    entity_json = json.loads(load_text(json_path))
    expected_ttl = normalize_ttl(load_text(ttl_path))

    actual_ttl = normalize_ttl(
        entity_to_ttl(entity_json)
    )

    expected_blocks = split_subject_blocks(expected_ttl)
    actual_blocks = split_subject_blocks(actual_ttl)

    # 1. Same subjects exist
    assert expected_blocks.keys() == actual_blocks.keys()

    # 2. Each subject block matches exactly
    for subject in expected_blocks:
        assert actual_blocks[subject] == expected_blocks[subject], (
            f"Mismatch in subject block: {subject}"
        )

def test_geo_coordinate_wkt():
    ttl = entity_to_ttl(
        json.loads(load_text(JSON_DIR / "Q120248304.json"))
    )

    assert '"Point(1.88108 50.94636)"^^geo:wktLiteral' in ttl

def test_monolingual_text_language_tag():
    ttl = entity_to_ttl(
        json.loads(load_text(JSON_DIR / "Q120248304.json"))
    )

    assert '"salle COSEC Saint-Exupéry"@fr' in ttl

def test_statement_with_qualifier():
    ttl = entity_to_ttl(
        json.loads(load_text(JSON_DIR / "Q120248304.json"))
    )

    assert "pq:P1810" in ttl
    assert '"Salle Cosec Saint Exupery"' in ttl

