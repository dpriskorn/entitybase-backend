#!/usr/bin/env python3
"""Download missing entity metadata files for test data."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.rdf_builder.entity_cache import load_entity_metadata_batch

# Remaining missing entities from Q1 after first download (still need metadata)
q1_remaining = [
    "Q109763642",
    "Q13165295",
    "Q18710250",
    "Q20966898",
    "Q22924128",
    "Q25636749",
    "Q28530019",
    "Q97272390",
]

# Combine all missing entities
all_missing = q1_remaining
print(f"Will download metadata for {len(all_missing)} entities")

# Filter out already downloaded
metadata_dir = Path("test_data/entity_metadata")
to_download = []
for entity_id in all_missing:
    if not (metadata_dir / f"{entity_id}.json").exists():
        to_download.append(entity_id)

if not to_download:
    print("All metadata files already exist!")
    exit(0)

print(f"Need to download {len(to_download)} entities")

# Download
results = load_entity_metadata_batch(to_download, metadata_dir)

# Report results
success_count = sum(1 for v in results.values() if v)
failed_count = sum(1 for v in results.values() if not v)

print("\nDownload complete:")
print(f"  Success: {success_count}")
print(f"  Failed: {failed_count}")

if failed_count > 0:
    print("\nFailed entities:")
    for entity_id, success in results.items():
        if not success:
            print(f"  - {entity_id}")
