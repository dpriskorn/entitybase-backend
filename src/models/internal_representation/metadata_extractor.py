import json
from typing import Any


class MetadataExtractor:
    """Extracts and prepares metadata (labels, descriptions, aliases) from entity JSON for deduplication."""

    @staticmethod
    def extract_labels(entity: dict[str, Any]) -> dict[str, dict[str, str]]:
        """Extract labels from entity JSON."""
        labels: dict[str, dict[str, str]] = entity.get("labels", {})
        return labels

    @staticmethod
    def extract_descriptions(entity: dict[str, Any]) -> dict[str, dict[str, str]]:
        """Extract descriptions from entity JSON."""
        descriptions: dict[str, dict[str, str]] = entity.get("descriptions", {})
        return descriptions

    @staticmethod
    def extract_aliases(entity: dict[str, Any]) -> dict[str, list[str]]:
        """Extract aliases from entity JSON."""
        aliases: dict[str, list[str]] = entity.get("aliases", {})
        return aliases

    @staticmethod
    def hash_metadata(metadata: Any) -> int:
        """Generate a hash for metadata content using rapidhash."""
        from rapidhash import rapidhash

        # Serialize to JSON for consistent hashing
        content = json.dumps(metadata, sort_keys=True, separators=(",", ":"))
        hash_value: int = rapidhash(content.encode("utf-8"))
        return hash_value

    @staticmethod
    def create_s3_key(metadata_type: str, content_hash: int) -> str:
        """Create S3 key for metadata storage."""
        return f"metadata/{metadata_type}/{content_hash}.json"
