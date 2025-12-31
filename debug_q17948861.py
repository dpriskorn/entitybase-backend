#!/usr/bin/env python3
import json
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.json_parser.entity_parser import parse_entity
from models.rdf_builder.converter import EntityConverter
from models.rdf_builder.property_registry.registry import PropertyRegistry
from models.rdf_builder.ontology.datatypes import property_shape

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

entity_id = "Q17948861"

# Paths
json_path = Path("test_data/json/entities") / f"{entity_id}.json"
ttl_path = Path("test_data/rdf/ttl") / f"{entity_id}.ttl"
metadata_dir = Path("test_data/entity_metadata")

# Parse JSON and generate TTL
entity_json = json.loads(json_path.read_text(encoding="utf-8"))
entity = parse_entity(entity_json)

properties = {
    "P31": property_shape("P31", "wikibase-item", labels={"en": {"language": "en", "value": "instance of"}}),
}
registry = PropertyRegistry(properties=properties)

converter = EntityConverter(property_registry=registry, entity_metadata_dir=metadata_dir)
actual_ttl = converter.convert_to_string(entity)

# Load golden TTL
golden_ttl = ttl_path.read_text(encoding="utf-8")

# Split into blocks
actual_blocks = split_subject_blocks(actual_ttl)
golden_blocks = split_subject_blocks(golden_ttl)

print(f"\nActual blocks ({len(actual_blocks)}):")
for key in sorted(actual_blocks.keys()):
    print(f"  {key}")

print(f"\nGolden blocks ({len(golden_blocks)}):")
for key in sorted(golden_blocks.keys()):
    print(f"  {key}")

print(f"\nMissing blocks:")
missing = set(golden_blocks.keys()) - set(actual_blocks.keys())
for key in sorted(missing):
    print(f"  {key}")

print(f"\nExtra blocks:")
extra = set(actual_blocks.keys()) - set(golden_blocks.keys())
for key in sorted(extra):
    print(f"  {key}")

print(f"\n\nGenerated TTL:")
print(actual_ttl)
