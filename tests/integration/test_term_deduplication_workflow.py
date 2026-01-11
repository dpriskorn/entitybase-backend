import unittest
from unittest.mock import Mock, patch, MagicMock
import json


# Mock rapidhash since it's not available in test environment
def mock_rapidhash(data):
    """Mock rapidhash implementation using built-in hash"""
    return hash(data) & 0xFFFFFFFFFFFFFFFF  # 64-bit mask


# Apply the mock
import sys

sys.modules["rapidhash"] = Mock()
sys.modules["rapidhash"].rapidhash = mock_rapidhash  # type: ignore[attr-defined]


class TestTermDeduplicationIntegration(unittest.TestCase):
    """Integration tests for the complete term deduplication system"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock all external dependencies
        self.mock_vitess_client = Mock()
        self.mock_s3_client = Mock()
        self.mock_terms_repo = Mock()

        # Mock connection manager for TermsRepository
        self.mock_conn_manager = Mock()

    def test_full_term_workflow(self):
        """Test the complete workflow from term extraction to storage and retrieval"""
        # Test data
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

        # Step 1: Extract terms
        from models.internal_representation.metadata_extractor import MetadataExtractor

        labels = MetadataExtractor.extract_labels(entity_data)
        descriptions = MetadataExtractor.extract_descriptions(entity_data)
        aliases = MetadataExtractor.extract_aliases(entity_data)

        expected_labels = {"en": "Douglas Adams", "fr": "Douglas Adams"}
        expected_descriptions = {"en": "English writer and comedian"}
        expected_aliases = {"en": ["DNA", "42"]}

        self.assertEqual(labels, expected_labels)
        self.assertEqual(descriptions, expected_descriptions)
        self.assertEqual(aliases, expected_aliases)

        # Step 2: Hash terms
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

        # Verify hashes are integers
        self.assertIsInstance(label_hashes["en"], int)
        self.assertIsInstance(description_hashes["en"], int)
        self.assertIsInstance(alias_hashes["en"][0], int)

        # Step 3: Mock storage operations
        # Labels/aliases stored in Vitess
        self.mock_terms_repo.insert_term = Mock()
        self.mock_terms_repo.insert_term.return_value = None

        # Descriptions stored in S3
        self.mock_s3_client.store_metadata = Mock()
        self.mock_s3_client.store_metadata.return_value = None

        # Step 4: Mock retrieval
        self.mock_terms_repo.get_term = Mock()
        self.mock_terms_repo.get_term.side_effect = lambda h: {
            label_hashes["en"]: ("Douglas Adams", "label"),
            label_hashes["fr"]: ("Douglas Adams", "label"),
            alias_hashes["en"][0]: ("DNA", "alias"),
            alias_hashes["en"][1]: ("42", "alias"),
        }.get(h)

        self.mock_s3_client.load_metadata = Mock()
        self.mock_s3_client.load_metadata.side_effect = lambda key, h: {
            description_hashes["en"]: "English writer and comedian"
        }.get(h)

        # Step 5: Test reconstruction
        # Reconstruct labels
        reconstructed_labels = {}
        for lang, hash_val in label_hashes.items():
            term_data = self.mock_terms_repo.get_term(hash_val)
            if term_data:
                term, term_type = term_data
                reconstructed_labels[lang] = {"language": lang, "value": term}

        # Reconstruct descriptions
        reconstructed_descriptions = {}
        for lang, hash_val in description_hashes.items():
            term = self.mock_s3_client.load_metadata("descriptions", hash_val)
            if term:
                reconstructed_descriptions[lang] = {"language": lang, "value": term}

        # Reconstruct aliases
        reconstructed_aliases = {}
        for lang, hash_list in alias_hashes.items():
            reconstructed_aliases[lang] = []
            for hash_val in hash_list:
                term_data = self.mock_terms_repo.get_term(hash_val)
                if term_data:
                    term, term_type = term_data
                    reconstructed_aliases[lang].append(
                        {"language": lang, "value": term}
                    )

        # Verify reconstruction
        self.assertEqual(
            reconstructed_labels,
            {
                "en": {"language": "en", "value": "Douglas Adams"},
                "fr": {"language": "fr", "value": "Douglas Adams"},
            },
        )

        self.assertEqual(
            reconstructed_descriptions,
            {"en": {"language": "en", "value": "English writer and comedian"}},
        )

        self.assertEqual(
            reconstructed_aliases,
            {
                "en": [
                    {"language": "en", "value": "DNA"},
                    {"language": "en", "value": "42"},
                ]
            },
        )

    def test_deduplication_benefit(self):
        """Test that identical terms get the same hash (deduplication)"""
        from models.internal_representation.metadata_extractor import MetadataExtractor

        # Same term in different contexts should hash identically
        term1 = "Douglas Adams"
        term2 = "Douglas Adams"

        hash1 = MetadataExtractor.hash_string(term1)
        hash2 = MetadataExtractor.hash_string(term2)

        self.assertEqual(
            hash1, hash2, "Identical terms should produce identical hashes"
        )

        # Different terms should hash differently
        term3 = "Douglas Noel Adams"
        hash3 = MetadataExtractor.hash_string(term3)

        self.assertNotEqual(
            hash1, hash3, "Different terms should produce different hashes"
        )

    def test_schema_validation(self):
        """Test that revision data conforms to schema 2.0.0"""
        import json

        # Sample revision data
        revision_data = {
            "schema_version": "2.0.0",
            "revision_id": 123,
            "created_at": "2024-01-01T00:00:00Z",
            "created_by": "test",
            "entity_type": "item",
            "entity": {"id": "Q42", "type": "item", "claims": {}},
            "labels_hashes": {"en": 12345, "fr": 67890},
            "descriptions_hashes": {"en": 11111},
            "aliases_hashes": {"en": [22222, 33333]},
        }

        # Convert to JSON string and back to ensure serializable
        json_str = json.dumps(revision_data)
        parsed = json.loads(json_str)

        # Verify structure
        self.assertEqual(parsed["schema_version"], "2.0.0")
        self.assertIn("labels_hashes", parsed)
        self.assertIn("descriptions_hashes", parsed)
        self.assertIn("aliases_hashes", parsed)
        self.assertIsInstance(parsed["labels_hashes"]["en"], int)
        self.assertIsInstance(parsed["aliases_hashes"]["en"], list)


if __name__ == "__main__":
    unittest.main()
