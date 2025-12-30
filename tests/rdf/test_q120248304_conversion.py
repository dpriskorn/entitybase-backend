import json
import logging

import pytest

from models.rdf_builder.converter import EntityConverter
from models.json_parser.entity_parser import parse_entity
from models.rdf_builder.property_registry.registry import PropertyRegistry
from models.rdf_builder.ontology.datatypes import property_shape
from conftest import TEST_DATA_DIR

logger = logging.getLogger(__name__)


def test_q120248304_conversion():
    """Test Q120248304 (medium entity) conversion produces valid Turtle"""
    entity_id = "Q120248304"

    json_path = TEST_DATA_DIR / "json" / "entities" / f"{entity_id}.json"

    entity_json = json.loads(json_path.read_text(encoding="utf-8"))
    entity = parse_entity(entity_json)

    logger.info(f"Parsed entity: {entity.id}, statements: {len(entity.statements)}")

    # Create property registry with properties from Q120248304
    properties = {
        "P31": property_shape("P31", "wikibase-item"),
        "P17": property_shape("P17", "wikibase-item"),
        "P127": property_shape("P127", "wikibase-item"),
        "P131": property_shape("P131", "wikibase-item"),
        "P137": property_shape("P137", "wikibase-item"),
        "P912": property_shape("P912", "wikibase-item"),
        "P248": property_shape("P248", "wikibase-item"),
        "P11840": property_shape("P11840", "external-id"),
        "P1810": property_shape("P1810", "string"),
        "P2561": property_shape("P2561", "monolingualtext"),
        "P5017": property_shape("P5017", "time"),
        "P625": property_shape("P625", "globe-coordinate"),
        "P6375": property_shape("P6375", "monolingualtext"),
    }
    registry = PropertyRegistry(properties=properties)

    converter = EntityConverter(property_registry=registry)
    actual_ttl = converter.convert_to_string(entity)

    logger.info(f"Generated TTL length: {len(actual_ttl)}")

    # Basic validation
    assert len(actual_ttl) > 0
    assert "wd:Q120248304" in actual_ttl

    # Check statement URIs use wds: prefix with dash separator
    assert "wds:Q120248304-4DFA2BE2-34CB-442E-B364-D01FE69A2FB5" in actual_ttl
    assert "$" not in actual_ttl, "Statement URIs should not contain $ separator"

    # Check reference URIs use wdref: prefix with hash
    assert "wdref:ba8e2620a184969d3dfc41448810665dc67de68e" in actual_ttl

    # Check some statement values
    assert "ps:P17 wd:Q142" in actual_ttl
    assert "ps:P11840 \"I621930023\"" in actual_ttl
    assert "ps:P625 \"Point(1.88108 50.94636)\"" in actual_ttl

    logger.info("Q120248304 conversion test passed!")
