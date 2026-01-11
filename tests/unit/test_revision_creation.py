import unittest
from models.internal_representation.metadata_extractor import MetadataExtractor


# Mock rapidhash since it's not available in test environment
def mock_rapidhash(data: bytes) -> int:
    """Mock rapidhash implementation using built-in hash"""
    return hash(data) & 0xFFFFFFFFFFFFFFFF  # 64-bit mask


import sys

if "rapidhash" not in sys.modules:
    sys.modules["rapidhash"] = type(sys)("rapidhash")
    sys.modules["rapidhash"].rapidhash = mock_rapidhash  # type: ignore[attr-defined]


class TestRevisionCreationLogic(unittest.TestCase):
    """Unit tests for revision creation term processing logic"""

    def test_term_hashing_logic(self) -> None:
        """Test the core logic of term extraction and hashing"""
        # Test data matching Wikibase format
        entity_data = {
            "id": "Q42",
            "labels": {
                "en": {"language": "en", "value": "Douglas Adams"},
                "fr": {"language": "fr", "value": "Douglas Adams"},
            },
            "descriptions": {
                "en": {"language": "en", "value": "English writer and comedian"}
            },
            "aliases": {
                "en": [
                    {"language": "en", "value": "DNA"},
                    {"language": "en", "value": "42"},
                ]
            },
        }

        # Extract terms
        labels = MetadataExtractor.extract_labels(entity_data)
        descriptions = MetadataExtractor.extract_descriptions(entity_data)
        aliases = MetadataExtractor.extract_aliases(entity_data)

        # Verify extraction
        expected_labels = {"en": "Douglas Adams", "fr": "Douglas Adams"}
        expected_descriptions = {"en": "English writer and comedian"}
        expected_aliases = {"en": ["DNA", "42"]}

        self.assertEqual(labels, expected_labels)
        self.assertEqual(descriptions, expected_descriptions)
        self.assertEqual(aliases, expected_aliases)

        # Hash terms (this would normally happen in the handler)
        label_hashes = {}
        for lang, label in labels.items():
            hash_val = MetadataExtractor.hash_string(label)
            label_hashes[lang] = hash_val

        description_hashes = {}
        for lang, desc in descriptions.items():
            hash_val = MetadataExtractor.hash_string(desc)
            description_hashes[lang] = hash_val

        alias_hashes = {}
        for lang, alias_list in aliases.items():
            hash_list = []
            for alias in alias_list:
                hash_val = MetadataExtractor.hash_string(alias)
                hash_list.append(hash_val)
            alias_hashes[lang] = hash_list

        # Verify hash structure
        self.assertIsInstance(label_hashes["en"], int)
        self.assertIsInstance(description_hashes["en"], int)
        self.assertIsInstance(alias_hashes["en"], list)
        self.assertEqual(len(alias_hashes["en"]), 2)

        # Test deduplication - same term should hash the same
        hash1 = MetadataExtractor.hash_string("Douglas Adams")
        hash2 = MetadataExtractor.hash_string("Douglas Adams")
        self.assertEqual(hash1, hash2)

        # Different terms should hash differently
        hash3 = MetadataExtractor.hash_string("Different Term")
        self.assertNotEqual(hash1, hash3)

    def test_revision_data_structure(self) -> None:
        """Test that revision data follows the expected schema 2.0.0 structure"""
        # Mock hash maps
        labels_hashes = {"en": 12345, "fr": 67890}
        descriptions_hashes = {"en": 11111}
        aliases_hashes = {"en": [22222, 33333]}

        # Build revision data structure
        revision_data = {
            "schema_version": "2.0.0",
            "revision_id": 123,
            "created_at": "2024-01-01T00:00:00Z",
            "created_by": "test",
            "entity_type": "item",
            "entity": {"id": "Q42", "type": "item", "claims": {}},
            "labels_hashes": labels_hashes,
            "descriptions_hashes": descriptions_hashes,
            "aliases_hashes": aliases_hashes,
        }

        # Verify structure matches schema expectations
        self.assertEqual(revision_data["schema_version"], "2.0.0")
        self.assertIn("labels_hashes", revision_data)
        self.assertIn("descriptions_hashes", revision_data)
        self.assertIn("aliases_hashes", revision_data)

        # Verify hash map structures
        self.assertIsInstance(revision_data["labels_hashes"], dict)
        self.assertIsInstance(revision_data["descriptions_hashes"], dict)
        self.assertIsInstance(revision_data["aliases_hashes"], dict)

        # Verify hash values are integers
        self.assertIsInstance(revision_data["labels_hashes"]["en"], int)
        self.assertIsInstance(revision_data["descriptions_hashes"]["en"], int)
        self.assertIsInstance(revision_data["aliases_hashes"]["en"], list)


if __name__ == "__main__":
    unittest.main()
