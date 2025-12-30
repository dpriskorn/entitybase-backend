import json
import logging

import pytest

from pathlib import Path

from models.rdf_builder.converter import EntityConverter
from models.json_parser.entity_parser import parse_entity
from models.rdf_builder.property_registry.registry import PropertyRegistry
from models.rdf_builder.ontology.datatypes import property_shape
from conftest import TEST_DATA_DIR

logger = logging.getLogger(__name__)


def test_q42_conversion():
    """Test Q42 conversion produces valid Turtle"""
    entity_id = "Q42"

    json_path = TEST_DATA_DIR / "json" / "entities" / f"{entity_id}.json"

    entity_json = json.loads(json_path.read_text(encoding="utf-8"))
    entity = parse_entity(entity_json)

    logger.info(f"Parsed entity: {entity.id}, statements: {len(entity.statements)}")

    # Create property registry with all properties from Q42
    properties = {
        "P31": property_shape("P31", "wikibase-item"),
        "P21": property_shape("P21", "wikibase-item"),
        "P106": property_shape("P106", "wikibase-item"),
    }
    registry = PropertyRegistry(properties=properties)

    converter = EntityConverter(property_registry=registry)
    actual_ttl = converter.convert_to_string(entity)

    logger.info(f"Generated TTL length: {len(actual_ttl)}")

    # Basic validation
    assert len(actual_ttl) > 0
    assert "wd:Q42" in actual_ttl
    assert "wds:Q42-F078E5B3-F9A8-480E-B7AC-D97778CBBEF9" in actual_ttl

    # Check reference URIs use wdref: format
    assert "wdref:a4d108601216cffd2ff1819ccf12b483486b62e7" in actual_ttl

    logger.info("Q42 conversion test passed!")
