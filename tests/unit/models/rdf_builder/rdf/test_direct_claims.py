import os
from io import StringIO
from pathlib import Path

from models.json_parser.entity_parser import parse_entity
from models.rdf_builder.converter import EntityConverter
from models.rdf_builder.ontology.datatypes import property_shape
from models.rdf_builder.property_registry.registry import PropertyRegistry
from models.rdf_builder.writers.triple import TripleWriters

TEST_DATA_DIR = Path(os.environ["TEST_DATA_DIR"])


def test_write_direct_claim_basic() -> None:
    """Test writing a direct claim triple"""
    output = StringIO()
    TripleWriters.write_direct_claim(output, "Q42", "P31", "wd:Q5")

    result = output.getvalue()
    assert "wd:Q42 wdt:P31 wd:Q5" in result
    assert result.count("wdt:P31") == 1


def test_write_direct_claim_entity_value() -> None:
    """Test direct claim with entity value"""
    output = StringIO()
    TripleWriters.write_direct_claim(output, "Q17948861", "P31", "wd:Q17633526")

    result = output.getvalue()
    assert "wd:Q17948861 wdt:P31 wd:Q17633526" in result


def test_entity_converter_generates_direct_claims_for_best_rank() -> None:
    """Test that EntityConverter generates direct claims for best-rank statements"""
    entity_id = "Q17948861"
    json_path = TEST_DATA_DIR / "json" / "entities" / f"{entity_id}.json"

    import json

    entity_json = json.loads(json_path.read_text(encoding="utf-8"))
    entity = parse_entity(entity_json)

    properties = {
        "P31": property_shape("P31", "wikibase-item"),
    }
    registry = PropertyRegistry(properties=properties)

    converter = EntityConverter(property_registry=registry)
    actual_ttl = converter.convert_to_string(entity)

    assert "wd:Q17948861 wdt:P31 wd:Q17633526" in actual_ttl
    assert "wdt:P31" in actual_ttl

