#!/usr/bin/env python3
import json
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.json_parser.entity_parser import parse_entity
from models.rdf_builder.converter import EntityConverter
from models.rdf_builder.property_registry.loader import load_property_registry

# Simple block splitter
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
            current_subject = line.split()[0]
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_subject:
        blocks[current_subject] = "\n".join(current_lines).strip()

    return blocks

entity_id = "Q42"

# Paths
json_path = Path("test_data/json/entities") / f"{entity_id}.json"
ttl_path = Path("test_data/rdf/ttl") / f"{entity_id}.ttl"
metadata_dir = Path("test_data/entity_metadata")
properties_dir = Path("test_data/properties")

# Parse JSON and generate TTL
entity_json = json.loads(json_path.read_text(encoding="utf-8"))
entity = parse_entity(entity_json)

# Load all properties from test_data/properties/
print(f"Loading property registry from {properties_dir}...")
registry = load_property_registry(properties_dir)
print(f"Loaded {len(registry.properties)} properties")

converter = EntityConverter(property_registry=registry, entity_metadata_dir=metadata_dir)
actual_ttl = converter.convert_to_string(entity)

# Load golden TTL
golden_ttl = ttl_path.read_text(encoding="utf-8")

# Split into blocks
actual_blocks = split_subject_blocks(actual_ttl)
golden_blocks = split_subject_blocks(golden_ttl)

missing = set(golden_blocks.keys()) - set(actual_blocks.keys())
extra = set(actual_blocks.keys()) - set(golden_blocks.keys())

# Write comparison to file
comparison_file = Path(__file__).parent / f"debug_{entity_id}_comparison.txt"
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
output_file = Path(__file__).parent / f"debug_{entity_id}_generated.ttl"
output_file.write_text(actual_ttl, encoding="utf-8")

print(f"Comparison written to: {comparison_file}")
print(f"Full TTL written to: {output_file}")

