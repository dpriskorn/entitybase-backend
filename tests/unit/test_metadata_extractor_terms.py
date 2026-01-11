import unittest
from unittest.mock import patch
from models.internal_representation.metadata_extractor import (
    MetadataExtractor,
    LabelsResponse,
    DescriptionsResponse,
)


class TestMetadataExtractor(unittest.TestCase):
    """Unit tests for MetadataExtractor term extraction and hashing"""

    def test_extract_labels(self) -> None:
        """Test extracting labels from entity JSON"""
        entity = {
            "labels": {
                "en": {"language": "en", "value": "Douglas Adams"},
                "fr": {"language": "fr", "value": "Douglas Adams"},
            }
        }
        result = MetadataExtractor.extract_labels(entity)
        expected = LabelsResponse(labels={"en": "Douglas Adams", "fr": "Douglas Adams"})
        self.assertEqual(result, expected)

    def test_extract_labels_empty(self):
        """Test extracting labels when none exist"""
        entity = {}
        result = MetadataExtractor.extract_labels(entity)
        self.assertEqual(result, LabelsResponse(labels={}))

    def test_extract_descriptions(self) -> None:
        """Test extracting descriptions from entity JSON"""
        entity = {
            "descriptions": {
                "en": {"language": "en", "value": "English writer"},
                "fr": {"language": "fr", "value": "Écrivain anglais"},
            }
        }
        result = MetadataExtractor.extract_descriptions(entity)
        expected = DescriptionsResponse(
            descriptions={"en": "English writer", "fr": "Écrivain anglais"}
        )
        self.assertEqual(result, expected)

    def test_extract_descriptions_empty(self):
        """Test extracting descriptions when none exist"""
        entity = {}
        result = MetadataExtractor.extract_descriptions(entity)
        self.assertEqual(result, DescriptionsResponse(descriptions={}))

    def test_extract_aliases(self):
        """Test extracting aliases from entity JSON"""
        entity = {
            "aliases": {
                "en": [
                    {"language": "en", "value": "DNA"},
                    {"language": "en", "value": "42"},
                ],
                "fr": [
                    {"language": "fr", "value": "ADN"},
                ],
            }
        }
        result = MetadataExtractor.extract_aliases(entity)
        expected = {"en": ["DNA", "42"], "fr": ["ADN"]}
        self.assertEqual(result, expected)

    def test_extract_aliases_empty(self):
        """Test extracting aliases when none exist"""
        entity = {}
        result = MetadataExtractor.extract_aliases(entity)
        self.assertEqual(result, {})

    def test_extract_aliases_malformed(self):
        """Test extracting aliases with missing value fields"""
        entity = {
            "aliases": {
                "en": [
                    {"language": "en", "value": "DNA"},
                    {"language": "en"},  # Missing value
                ],
            }
        }
        result = MetadataExtractor.extract_aliases(entity)
        expected = {"en": ["DNA"]}
        self.assertEqual(result, expected)

    @patch("rapidhash.rapidhash")
    def test_hash_string(self, mock_rapidhash):
        """Test hashing a string"""
        mock_rapidhash.return_value = 12345
        result = MetadataExtractor.hash_string("test string")
        self.assertEqual(result, 12345)
        mock_rapidhash.assert_called_once_with(b"test string")

    @patch("rapidhash.rapidhash")
    def test_hash_metadata_deprecated(self, mock_rapidhash):
        """Test the deprecated hash_metadata method"""
        mock_rapidhash.return_value = 67890
        result = MetadataExtractor.hash_metadata({"test": "data"})
        self.assertEqual(result, 67890)
        # Should have JSON serialized the input
        mock_rapidhash.assert_called_once()
        call_args = mock_rapidhash.call_args[0][0]
        self.assertIsInstance(call_args, bytes)

    def test_create_s3_key(self):
        """Test creating S3 key for metadata storage"""
        result = MetadataExtractor.create_s3_key("labels", 12345)
        expected = "metadata/labels/12345.json"
        self.assertEqual(result, expected)
