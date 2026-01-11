from models.internal_representation.metadata_extractor import (
    MetadataExtractor,
    LabelsResponse,
    DescriptionsResponse,
)


class TestMetadataExtractor:
    def test_extract_labels(self) -> None:
        """Test extracting labels from entity JSON."""
        entity = {
            "id": "Q1",
            "labels": {
                "en": {"language": "en", "value": "Test Entity"},
                "de": {"language": "de", "value": "Test Entität"},
            },
            "descriptions": {},
            "aliases": {},
        }

        result = MetadataExtractor.extract_labels(entity)
        expected = LabelsResponse(
            labels={
                "en": "Test Entity",
                "de": "Test Entität",
            }
        )
        assert result == expected

    def test_extract_descriptions(self) -> None:
        """Test extracting descriptions from entity JSON."""
        entity = {
            "id": "Q1",
            "labels": {},
            "descriptions": {
                "en": {"language": "en", "value": "A test entity"},
                "de": {"language": "de", "value": "Eine Testentität"},
            },
            "aliases": {},
        }

        result = MetadataExtractor.extract_descriptions(entity)
        expected = DescriptionsResponse(
            descriptions={
                "en": "A test entity",
                "de": "Eine Testentität",
            }
        )
        assert result == expected

    def test_extract_aliases(self) -> None:
        """Test extracting aliases from entity JSON."""
        entity = {
            "id": "Q1",
            "labels": {},
            "descriptions": {},
            "aliases": {"en": ["Test", "Example"], "de": ["Test", "Beispiel"]},
        }

        result = MetadataExtractor.extract_aliases(entity)
        expected = {"en": ["Test", "Example"], "de": ["Test", "Beispiel"]}
        assert result == expected

    def test_extract_missing_metadata(self) -> None:
        """Test extracting from entity without metadata."""
        entity = {"id": "Q1"}

        assert MetadataExtractor.extract_labels(entity) == LabelsResponse(labels={})
        assert MetadataExtractor.extract_descriptions(entity) == DescriptionsResponse(
            descriptions={}
        )
        assert MetadataExtractor.extract_aliases(entity) == {}

    def test_hash_metadata(self) -> None:
        """Test hashing metadata."""
        metadata = {"en": {"language": "en", "value": "Test"}}

        hash1 = MetadataExtractor.hash_metadata(metadata)
        hash2 = MetadataExtractor.hash_metadata(metadata)

        assert isinstance(hash1, int)
        assert hash1 == hash2  # Same metadata should hash the same

        # Different metadata should hash differently
        different_metadata = {"en": {"language": "en", "value": "Different"}}
        hash3 = MetadataExtractor.hash_metadata(different_metadata)
        assert hash1 != hash3

    def test_create_s3_key(self) -> None:
        """Test creating S3 key for metadata."""
        key = MetadataExtractor.create_s3_key("labels", 12345)
        assert key == "metadata/labels/12345.json"

    def test_hash_metadata_consistency(self) -> None:
        """Test that hash is consistent for same data."""
        data = {"test": "value", "number": 42}

        # Order shouldn't matter for hashing
        data_reordered = {"number": 42, "test": "value"}

        hash1 = MetadataExtractor.hash_metadata(data)
        hash2 = MetadataExtractor.hash_metadata(data_reordered)

        assert hash1 == hash2
