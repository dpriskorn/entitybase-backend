"""Integration test for value node deduplication in entity conversion."""

import json
import logging
import os
from pathlib import Path
from typing import Any

from models.json_parser.entity_parser import parse_entity
from models.rdf_builder.converter import EntityConverter

TEST_DATA_DIR = Path(os.environ["TEST_DATA_DIR"])

logger = logging.getLogger(__name__)


def test_deduplication_stats(full_property_registry: Any) -> None:
    """Test that deduplication statistics are tracked."""
    entity_id = "Q120248304"

    json_path = TEST_DATA_DIR / "json" / "entities" / f"{entity_id}.json"
    entity_json = json.loads(json_path.read_text(encoding="utf-8"))
    entity = parse_entity(entity_json)

    converter = EntityConverter(property_registry=full_property_registry)
    converter.convert_to_string(entity)

    # Check stats are available
    if converter.dedupe:
        stats = converter.dedupe.stats()
        logger.info(f"Deduplication stats: {stats}")

        assert stats["hits"] >= 0
        assert stats["misses"] >= 0
        assert stats["size"] >= 0
        assert 0 <= stats["collision_rate"] <= 100


def test_deduplication_disabled(full_property_registry: Any) -> None:
    """Test that deduplication can be disabled."""
    entity_id = "Q120248304"

    json_path = TEST_DATA_DIR / "json" / "entities" / f"{entity_id}.json"
    entity_json = json.loads(json_path.read_text(encoding="utf-8"))
    entity = parse_entity(entity_json)

    # Create converter with deduplication disabled
    converter = EntityConverter(
        property_registry=full_property_registry, enable_deduplication=False
    )

    assert converter.dedupe is None, "Dedupe should be None when disabled"

    # Should still generate valid TTL
    actual_ttl = converter.convert_to_string(entity)
    assert len(actual_ttl) > 0
    assert "wd:Q120248304" in actual_ttl


