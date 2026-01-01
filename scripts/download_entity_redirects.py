#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.rdf_builder.redirect_cache import load_entity_redirects_batch


def find_entities_with_redirects(entities_dir: Path) -> list[str]:
    """Find all entities in test data."""
    entity_files = sorted(f.stem for f in entities_dir.glob("Q*.json"))
    return entity_files


def main():
    entities_dir = Path(__file__).parent.parent / "test_data" / "json" / "entities"
    redirects_dir = Path(__file__).parent.parent / "test_data" / "entity_redirects"
    redirects_dir.mkdir(parents=True, exist_ok=True)

    entities = find_entities_with_redirects(entities_dir)

    if not entities:
        print("✅ No entities to fetch redirects for!")
        return

    print(f"Found {len(entities)} entities")

    load_entity_redirects_batch(entities, redirects_dir)

    print(f"✅ Downloaded redirects for {len(entities)} entities")


if __name__ == "__main__":
    main()
