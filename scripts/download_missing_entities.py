#!/usr/bin/env python3
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.rdf_builder.entity_cache import load_entity_metadata_batch


def find_missing_referenced_entities(entities_dir: Path) -> list[str]:
    """Find entity IDs referenced in test data but missing from cache."""
    existing = set(f.stem for f in entities_dir.glob("Q*.json"))
    referenced = set()

    for json_file in entities_dir.glob("Q*.json"):
        data = json.loads(json_file.read_text())
        for entity in data.get("entities", {}).values():
            for claims in entity.get("claims", {}).values():
                for claim in claims:
                    if "mainsnak" in claim and "datavalue" in claim["mainsnak"]:
                        datavalue = claim["mainsnak"]["datavalue"]
                        if datavalue.get("type") == "wikibase-entityid":
                            numeric_id = datavalue.get("value", {}).get("numeric-id")
                            if numeric_id:
                                entity_id = f"Q{numeric_id}"
                                referenced.add(entity_id)

    missing = referenced - existing
    return sorted(missing)


def main():
    entities_dir = Path(__file__).parent.parent / "test_data" / "json" / "entities"
    metadata_dir = Path(__file__).parent.parent / "test_data" / "entity_metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)

    missing = find_missing_referenced_entities(entities_dir)

    if not missing:
        print("✅ All referenced entities already have metadata!")
        return

    print(f"Found {len(missing)} entities missing metadata")

    load_entity_metadata_batch(missing, metadata_dir)

    print(f"✅ Downloaded metadata for {len(missing)} entities")


if __name__ == "__main__":
    main()
