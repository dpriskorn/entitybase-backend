"""Metadata extraction utilities for Wikibase entities."""

import json
from typing import Any

from pydantic import BaseModel

from models.rest_api.response.misc import AliasesDict


class LabelsResponse(BaseModel):
    """Response model for extracted labels."""

    labels: dict[str, str]


class DescriptionsResponse(BaseModel):
    """Response model for extracted descriptions."""

    descriptions: dict[str, str]


class MetadataExtractor:
    """Extracts and prepares metadata (labels, descriptions, aliases) from entity JSON for deduplication."""

    @staticmethod
    def extract_labels(entity: dict[str, Any]) -> LabelsResponse:
        """Extract label values from entity JSON."""
        labels = entity.get("labels", {})
        data = {
            lang: label_data["value"]
            for lang, label_data in labels.items()
            if "value" in label_data
        }
        return LabelsResponse(labels=data)

    @staticmethod
    def extract_descriptions(entity: dict[str, Any]) -> DescriptionsResponse:
        """Extract description values from entity JSON."""
        descriptions = entity.get("descriptions", {})
        data = {
            lang: desc_data["value"]
            for lang, desc_data in descriptions.items()
            if "value" in desc_data
        }
        return DescriptionsResponse(descriptions=data)

    @staticmethod
    def extract_aliases(entity: dict[str, Any]) -> AliasesDict:
        """Extract alias values from entity JSON."""
        aliases = entity.get("aliases", {})
        return AliasesDict(
            aliases={
                lang: [
                    alias_data["value"]
                    for alias_data in alias_list
                    if "value" in alias_data
                ]
                for lang, alias_list in aliases.items()
            }
        )

    @staticmethod
    def hash_string(content: str) -> int:
        """Generate a 64-bit rapidhash for a string."""
        from rapidhash import rapidhash

        return rapidhash(content.encode("utf-8"))

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
