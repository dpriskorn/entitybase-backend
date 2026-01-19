from typing import Any

from models.internal_representation.metadata_extractor import MetadataExtractor


class TestMetadataDeduplicationIntegration:
    """Integration tests for metadata deduplication functionality."""

    def test_metadata_deduplication_workflow(
        self, api_client: Any, base_url: str
    ) -> None:
        """Test complete metadata deduplication workflow."""
        # This is a placeholder for full integration testing
        # Would require:
        # 1. Create entity with labels/descriptions/aliases
        # 2. Verify metadata hashes are stored in entity_revisions
        # 3. Verify metadata is stored in S3 with deduplication
        # 4. Verify metadata is loaded correctly on read
        # 5. Verify ref counting works for duplicate metadata

        # For now, test the components individually
        entity_data = {
            "id": "Q999",
            "type": "item",
            "labels": {"en": {"language": "en", "value": "Test Entity"}},
            "descriptions": {"en": {"language": "en", "value": "A test entity"}},
            "aliases": {"en": ["Test", "Example"]},
            "claims": {},
        }

        # Test metadata extraction
        labels = MetadataExtractor.extract_labels(entity_data)
        descriptions = MetadataExtractor.extract_descriptions(entity_data)
        aliases = MetadataExtractor.extract_aliases(entity_data)

        assert labels.labels == {"en": "Test Entity"}
        assert descriptions.descriptions == {"en": "A test entity"}
        assert aliases == {"en": ["Test", "Example"]}

        # Test hashing
        labels_hash = MetadataExtractor.hash_metadata(labels)
        descriptions_hash = MetadataExtractor.hash_metadata(descriptions)
        aliases_hash = MetadataExtractor.hash_metadata(aliases)

        assert isinstance(labels_hash, int)
        assert isinstance(descriptions_hash, int)
        assert isinstance(aliases_hash, int)

        # Test S3 key generation
        labels_key = MetadataExtractor.create_s3_key("labels", labels_hash)
        descriptions_key = MetadataExtractor.create_s3_key(
            "descriptions", descriptions_hash
        )
        aliases_key = MetadataExtractor.create_s3_key("aliases", aliases_hash)

        assert labels_key.startswith("metadata/labels/")
        assert descriptions_key.startswith("metadata/descriptions/")
        assert aliases_key.startswith("metadata/aliases/")

        # Note: Full integration test would require running API
        # response = api_client.post(f"{base_url}/entity", json=entity_data)
        # assert response.status_code == 201

        # Then verify hashes in database and metadata in S3

    def test_metadata_hash_consistency(self) -> None:
        """Test that identical metadata produces same hash."""
        metadata1 = {
            "en": {"language": "en", "value": "Test"},
            "de": {"language": "de", "value": "Test"},
        }
        metadata2 = {
            "en": {"language": "en", "value": "Test"},
            "de": {"language": "de", "value": "Test"},
        }

        hash1 = MetadataExtractor.hash_metadata(metadata1)
        hash2 = MetadataExtractor.hash_metadata(metadata2)

        assert hash1 == hash2

    def test_metadata_hash_uniqueness(self) -> None:
        """Test that different metadata produces different hashes."""
        metadata1 = {"en": {"language": "en", "value": "Test1"}}
        metadata2 = {"en": {"language": "en", "value": "Test2"}}

        hash1 = MetadataExtractor.hash_metadata(metadata1)
        hash2 = MetadataExtractor.hash_metadata(metadata2)

        assert hash1 != hash2

    def test_metadata_deduplication_edge_cases(self) -> None:
        """Test metadata deduplication with edge cases."""
        # Empty metadata
        empty_hash = MetadataExtractor.hash_metadata({})
        assert isinstance(empty_hash, int)

        # Large metadata
        large_metadata = {
            f"lang{i}": {"language": f"lang{i}", "value": f"value{i}"}
            for i in range(100)
        }
        large_hash = MetadataExtractor.hash_metadata(large_metadata)
        assert isinstance(large_hash, int)

        # Special characters
        special_metadata = {
            "en": {"language": "en", "value": "Test with spécial chärs 🚀"}
        }
        special_hash = MetadataExtractor.hash_metadata(special_metadata)
        assert isinstance(special_hash, int)
