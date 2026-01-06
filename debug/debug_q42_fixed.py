"""Debug script to investigate Q42 deduplication issue."""

import sys

# Add project root to path
PROJECT_ROOT = "/home/dpriskorn/src/python/wikibase-backend"
sys.path.insert(0, PROJECT_ROOT)

import json
from pathlib import Path
from models.json_parser.entity_parser import parse_entity
from models.rdf_builder.converter import EntityConverter
from models.rdf_builder.property_registry.loader import load_property_registry

TEST_DATA_DIR = Path(PROJECT_ROOT, "test_data")


def debug_q42():
    """Debug Q42 deduplication in detail."""
    print("=" * 80)
    print("DEBUG: Q42 Deduplication Investigation")
    print("=" * 80)

    # Load entity
    entity_id = "Q42"
    json_path = TEST_DATA_DIR / "json" / "entities" / f"{entity_id}.json"
    entity_json = json.loads(json_path.read_text(encoding="utf-8"))
    entity = parse_entity(entity_json)

    print(f"\nEntity: {entity.id}")
    print(f"Statements: {len(entity.statements)}")

    # Load property registry
    registry = load_property_registry(TEST_DATA_DIR / "properties")

    # Convert with deduplication enabled
    print("\nConverting with deduplication...")
    converter = EntityConverter(property_registry=registry, enable_deduplication=True)
    actual_ttl = converter.convert_to_string(entity)

    # Count value node references
    import re

    wdv_refs = re.findall(r"wdv:([a-f0-9]{32})", actual_ttl)

    print("\nValue Node Statistics:")
    print(f"  Total wdv: refs: {len(wdv_refs)}")
    print(f"  Unique wdv: IDs: {len(set(wdv_refs))}")

    # Count duplicates
    from collections import Counter

    ref_counts = Counter(wdv_refs)
    duplicates = [hash_val for hash_val, count in ref_counts.items() if count > 1]

    print("\nDuplicate Value Nodes (appearing more than once):")
    for hash_val in sorted(set(duplicates))[:10]:
        count = ref_counts[hash_val]
        print(f"  wdv:{hash_val} - {count} times")

    print(f"\nTotal duplicate hashes: {len(set(duplicates))}")
    print(
        f"Total duplicate references: {sum(ref_counts.values()) - len(set(wdv_refs))}"
    )

    # Show deduplication stats
    if converter.dedupe:
        stats = converter.dedupe.stats()
        print("\nDeduplication Cache Stats:")
        print(f"  Hits (duplicates prevented): {stats['hits']}")
        print(f"  Misses (unique values): {stats['misses']}")
        print(f"  Cache size: {stats['size']}")
        print(f"  Collision rate: {stats['collision_rate']:.1f}%")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    debug_q42()
