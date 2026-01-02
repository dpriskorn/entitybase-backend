import json
import logging

from conftest import TEST_DATA_DIR
from models.json_parser.entity_parser import parse_entity
from models.rdf_builder.converter import EntityConverter

logger = logging.getLogger(__name__)


def test_q42_conversion(full_property_registry):
    """Test Q42 conversion produces valid Turtle"""
    entity_id = "Q42"

    json_path = TEST_DATA_DIR / "json" / "entities" / f"{entity_id}.json"

    entity_json = json.loads(json_path.read_text(encoding="utf-8"))
    entity = parse_entity(entity_json)

    logger.info(f"Parsed entity: {entity.id}, statements: {len(entity.statements)}")

    # Use full property registry from CSV cache
    converter = EntityConverter(property_registry=full_property_registry)
    actual_ttl = converter.convert_to_string(entity)

    logger.info(f"Generated TTL length: {len(actual_ttl)}")

    # Basic validation
    assert len(actual_ttl) > 0
    assert "wd:Q42" in actual_ttl
    assert "wds:Q42-F078E5B3-F9A8-480E-B7AC-D97778CBBEF9" in actual_ttl

    # Check reference URIs use wdref: format
    assert "wdref:a4d108601216cffd2ff1819ccf12b483486b62e7" in actual_ttl

    logger.info("Q42 conversion test passed!")
