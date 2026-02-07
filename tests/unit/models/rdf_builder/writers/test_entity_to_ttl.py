"""Test for entity to TTL conversion."""

import json
import logging
import re

from models.rdf_builder.converter import EntityConverter
from models.json_parser.entity_parser import parse_entity
import os
from pathlib import Path


def normalize_ttl(ttl: str) -> str:
    logger = logging.getLogger(__name__)
    logger.debug("=== normalize_ttl() START ===")
    logger.debug(f"Input length: {len(ttl)} chars")
    logger.debug(f"First 100 chars of input: {repr(ttl[:100])}")

    ttl = re.sub(r"#.*$", "", ttl, flags=re.MULTILINE)
    logger.debug(f"After removing comments: {len(ttl)} chars")

    ttl = re.sub(r"[ \t]+", " ", ttl)
    logger.debug(f"After normalizing whitespace: {len(ttl)} chars")
    logger.debug(f"First 100 chars: {repr(ttl[:100])}")

    ttl = re.sub(r"\n\n+", "\n\n", ttl)
    logger.debug(f"After normalizing newlines: {len(ttl)} chars")
    logger.debug(f"First 100 chars: {repr(ttl[:100])}")

    result = ttl.strip()
    logger.debug(f"Result length: {len(result)} chars")
    logger.debug(f"First 100 chars: {repr(result[:100])}")
    logger.debug("=== normalize_ttl() END ===")
    return result


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
TEST_DATA_DIR = Path(__file__).parent.parent / "test_data"


def test_q120248304_matches_golden_ttl(property_registry):
    entity_id = "Q120248304"

    json_path = TEST_DATA_DIR / "json" / "entities" / f"{entity_id}.json"
    ttl_path = TEST_DATA_DIR / "rdf" / "ttl" / f"{entity_id}.ttl"

    entity_json = json.loads(json_path.read_text(encoding="utf-8"))
    expected_ttl = normalize_ttl(ttl_path.read_text(encoding="utf-8"))

    # ✅ use the real, already-working parser
    entity = parse_entity(entity_json)

    converter = EntityConverter(property_registry=property_registry)
    actual_ttl = normalize_ttl(converter.convert_to_string(entity))

    expected_blocks = split_subject_blocks(expected_ttl)
    actual_blocks = split_subject_blocks(actual_ttl)

    logger.info(f"Expected blocks count: {len(expected_blocks)}")
    logger.info(f"Actual blocks count: {len(actual_blocks)}")
    logger.info(f"Expected block keys: {list(expected_blocks.keys())}")
    logger.info(f"Actual block keys: {list(actual_blocks.keys())}")

    assert expected_blocks.keys() == actual_blocks.keys()

    for subject in expected_blocks:
        assert actual_blocks[subject] == expected_blocks[subject]
