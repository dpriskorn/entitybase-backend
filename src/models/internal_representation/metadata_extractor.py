"""Metadata extraction utilities for Wikibase entities."""

import json
from typing import Any

from pydantic import BaseModel


class MetadataExtractor(BaseModel):
    """Extracts and prepares metadata (labels, descriptions, aliases) from entity JSON for deduplication."""

    @staticmethod
    def hash_string(content: str) -> int:
        """Generate a 64-bit rapidhash for a string."""
        from rapidhash import rapidhash

        return rapidhash(content.encode("utf-8"))  # type: ignore[no-any-return]

    @staticmethod
    def hash_metadata(metadata: Any) -> int:
        """Generate a hash for metadata content using rapidhash (deprecated - use hash_string for individual strings)."""
        from rapidhash import rapidhash

        # Serialize to JSON for consistent hashing
        content = json.dumps(metadata, sort_keys=True, separators=(",", ":"))
        hash_value: int = rapidhash(content.encode("utf-8"))
        return hash_value

    @staticmethod
    def create_s3_key(metadata_type: str, content_hash: int) -> str:
        """Create S3 key for metadata storage."""
        return f"metadata/{metadata_type}/{content_hash}.json"
