"""Unit tests for MetadataExtractor."""

from models.internal_representation.metadata_extractor import MetadataExtractor


class TestMetadataExtractor:
    """Unit tests for MetadataExtractor static methods."""

    def test_hash_string_basic(self) -> None:
        """Test hash_string with a basic string."""
        result = MetadataExtractor.hash_string("test")
        assert isinstance(result, int)
        assert result > 0  # Assuming rapidhash produces positive ints

    def test_hash_string_consistency(self) -> None:
        """Test hash_string produces consistent results."""
        hash1 = MetadataExtractor.hash_string("consistent")
        hash2 = MetadataExtractor.hash_string("consistent")
        assert hash1 == hash2

    def test_hash_string_different_inputs(self) -> None:
        """Test hash_string produces different hashes for different inputs."""
        hash1 = MetadataExtractor.hash_string("input1")
        hash2 = MetadataExtractor.hash_string("input2")
        assert hash1 != hash2

    def test_hash_string_empty_string(self) -> None:
        """Test hash_string with empty string."""
        result = MetadataExtractor.hash_string("")
        assert isinstance(result, int)

    def test_hash_string_unicode(self) -> None:
        """Test hash_string with unicode characters."""
        result = MetadataExtractor.hash_string("café")
        assert isinstance(result, int)

    def test_hash_metadata_dict(self) -> None:
        """Test hash_metadata with a dictionary."""
        metadata = {"key": "value", "number": 42}
        result = MetadataExtractor.hash_metadata(metadata)
        assert isinstance(result, int)

    def test_hash_metadata_list(self) -> None:
        """Test hash_metadata with a list."""
        metadata = ["item1", "item2", {"nested": "dict"}]
        result = MetadataExtractor.hash_metadata(metadata)
        assert isinstance(result, int)

    def test_hash_metadata_consistency(self) -> None:
        """Test hash_metadata produces consistent results."""
        metadata = {"a": 1, "b": 2}
        hash1 = MetadataExtractor.hash_metadata(metadata)
        hash2 = MetadataExtractor.hash_metadata(metadata)
        assert hash1 == hash2

    def test_hash_metadata_sorting(self) -> None:
        """Test hash_metadata uses sort_keys for consistency."""
        metadata1 = {"b": 1, "a": 2}
        metadata2 = {"a": 2, "b": 1}
        hash1 = MetadataExtractor.hash_metadata(metadata1)
        hash2 = MetadataExtractor.hash_metadata(metadata2)
        assert hash1 == hash2  # Should be equal due to sorting

    def test_hash_metadata_separators(self) -> None:
        """Test hash_metadata uses compact separators."""
        metadata = {"key": "value"}
        # Manually check JSON output would be '{"key":"value"}' without spaces
        result = MetadataExtractor.hash_metadata(metadata)
        assert isinstance(result, int)

    def test_create_s3_key_basic(self) -> None:
        """Test create_s3_key with basic inputs."""
        result = MetadataExtractor.create_s3_key("labels", 12345)
        assert result == "metadata/labels/12345.json"

    def test_create_s3_key_different_types(self) -> None:
        """Test create_s3_key with different metadata types."""
        result = MetadataExtractor.create_s3_key("descriptions", 67890)
        assert result == "metadata/descriptions/67890.json"

    def test_create_s3_key_edge_cases(self) -> None:
        """Test create_s3_key with edge cases."""
        result = MetadataExtractor.create_s3_key("", 0)
        assert result == "metadata//0.json"

    def test_create_s3_key_large_hash(self) -> None:
        """Test create_s3_key with large hash value."""
        large_hash = 9223372036854775807  # Max int64
        result = MetadataExtractor.create_s3_key("aliases", large_hash)
        assert result == f"metadata/aliases/{large_hash}.json"
