#!/usr/bin/env python3
"""Generic debug script for converting entity to TTL and comparing with golden file."""

import argparse
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.json_parser.entity_parser import parse_entity
from models.rdf_builder.converter import EntityConverter
from models.rdf_builder.property_registry.loader import load_property_registry


def split_subject_blocks(ttl: str) -> dict[str, str]:
    """Split Turtle file into subject-based blocks."""
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
            current_subject = line.split()[0]
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_subject:
        blocks[current_subject] = "\n".join(current_lines).strip()

    return blocks


def main():
    parser = argparse.ArgumentParser(description="Debug entity to TTL conversion")
    parser.add_argument("entity_id", help="Entity ID (e.g., Q42)")
    args = parser.parse_args()

    entity_id = args.entity_id

    # Paths
    json_path = (
        Path(__file__).parent.parent / f"test_data/json/entities/{entity_id}.json"
    )
    ttl_path = Path(__file__).parent.parent / f"test_data/rdf/ttl/{entity_id}.ttl"
    metadata_dir = Path(__file__).parent.parent / "test_data/entity_metadata"
    redirects_dir = Path(__file__).parent.parent / "test_data/entity_redirects"
    properties_dir = Path(__file__).parent.parent / "test_data/properties"

    # Check if required files exist
    if not json_path.exists():
        print(f"ERROR: Entity JSON not found: {json_path}")
        sys.exit(1)

    if not ttl_path.exists():
        print(f"ERROR: Golden TTL not found: {ttl_path}")
        sys.exit(1)

    # Parse JSON and generate TTL
    entity_json = json.loads(json_path.read_text(encoding="utf-8"))
    entity = parse_entity(entity_json)

    # Load all properties from test_data/properties/
    print(f"Loading property registry from {properties_dir}...")
    registry = load_property_registry(properties_dir)
    print(f"Loaded {len(registry.properties)} properties")

    converter = EntityConverter(
        property_registry=registry,
        entity_metadata_dir=metadata_dir,
        redirects_dir=redirects_dir,
    )
    actual_ttl = converter.convert_to_string(entity)

    # Load golden TTL
    golden_ttl = ttl_path.read_text(encoding="utf-8")

    # Split into blocks
    actual_blocks = split_subject_blocks(actual_ttl)
    golden_blocks = split_subject_blocks(golden_ttl)

    missing = set(golden_blocks.keys()) - set(actual_blocks.keys())
    extra = set(actual_blocks.keys()) - set(golden_blocks.keys())

    # Write comparison to file
    debug_dir = Path(__file__).parent
    comparison_file = debug_dir / f"debug_{entity_id}_comparison.txt"
    comparison_content = f"""
Actual blocks ({len(actual_blocks)}):
Golden blocks ({len(golden_blocks)}):

Missing blocks ({len(missing)} total):
{chr(10).join([f"  {key}" for key in sorted(missing)])}

Extra blocks ({len(extra)} total):
{chr(10).join([f"  {key}" for key in sorted(extra)])}
"""
    comparison_file.write_text(comparison_content.strip(), encoding="utf-8")

    # Write full TTL to separate file
    output_file = debug_dir / f"debug_{entity_id}_generated.ttl"
    output_file.write_text(actual_ttl, encoding="utf-8")

    print(f"Comparison written to: {comparison_file}")
    print(f"Full TTL written to: {output_file}")

    # Print summary
    print("\nSummary:")
    print(f"  Actual blocks: {len(actual_blocks)}")
    print(f"  Golden blocks: {len(golden_blocks)}")
    print(f"  Missing: {len(missing)}")
    print(f"  Extra: {len(extra)}")

    if missing or extra:
        sys.exit(1)


if __name__ == "__main__":
    main()
