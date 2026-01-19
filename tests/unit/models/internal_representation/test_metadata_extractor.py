from models.internal_representation.metadata_extractor import (
    MetadataExtractor,
    LabelsResponse,
    DescriptionsResponse,
    AliasesResponse,
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
            "aliases": {
                "en": [{"value": "Test"}, {"value": "Example"}],
                "de": [{"value": "Test"}, {"value": "Beispiel"}],
            },
        }

        result = MetadataExtractor.extract_aliases(entity)
        expected = AliasesResponse(
            aliases={"en": ["Test", "Example"], "de": ["Test", "Beispiel"]}
        )
        assert result == expected

    def test_extract_missing_metadata(self) -> None:
        """Test extracting from entity without metadata."""
        entity: dict[str, Any] = {"id": "Q1"}

        assert MetadataExtractor.extract_labels(entity) == LabelsResponse(labels={})
        assert MetadataExtractor.extract_descriptions(entity) == DescriptionsResponse(
            descriptions={}
        )
        assert MetadataExtractor.extract_aliases(entity) == AliasesResponse(aliases={})

    def test_hash_metadata(self) -> None:
        """Test hashing metadata."""
        metadata = {"en": {"language": "en", "value": "Test"}}

        hash1 = MetadataExtractor.hash_metadata(metadata)
        hash2 = MetadataExtractor.hash_metadata(metadata)

        assert isinstance(hash1, int)
        assert hash1 == hash2

    def test_hash_metadata_empty(self) -> None:
        """Test hashing empty metadata."""
        metadata: dict[str, Any] = {}

        hash_value = MetadataExtractor.hash_metadata(metadata)

        assert isinstance(hash_value, int)

    def test_hash_metadata_different(self) -> None:
        """Test hashing different metadata produces different hashes."""
        metadata1: dict[str, Any] = {"en": {"language": "en", "value": "Test1"}}
        metadata2: dict[str, Any] = {"en": {"language": "en", "value": "Test2"}}

        hash1 = MetadataExtractor.hash_metadata(metadata1)
        hash2 = MetadataExtractor.hash_metadata(metadata2)

        assert hash1 != hash2
