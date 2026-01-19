"""Unit tests for HashService."""

import unittest
from unittest.mock import MagicMock, patch
from models.rest_api.v1.entitybase.services.hash_service import HashService
from models.infrastructure.s3.hashes.labels_hashes import LabelsHashes
from models.infrastructure.s3.hashes.descriptions_hashes import DescriptionsHashes
from models.infrastructure.s3.hashes.aliases_hashes import AliasesHashes
from models.infrastructure.s3.hashes.sitelinks_hashes import SitelinksHashes
from models.infrastructure.s3.hashes.statements_hashes import StatementsHashes
from models.infrastructure.s3.hashes.hash_maps import HashMaps
from models.rest_api.v1.entitybase.response import StatementHashResult


class TestHashService(unittest.TestCase):
    """Unit tests for HashService."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_vitess = MagicMock()
        self.mock_s3 = MagicMock()
        self.mock_validator = MagicMock()

    @patch("models.rest_api.v1.entitybase.services.hash_service.hash_entity_statements")
    @patch(
        "models.rest_api.v1.entitybase.services.hash_service.deduplicate_and_store_statements"
    )
    def test_hash_statements_success(self, mock_store, mock_hash) -> None:
        """Test successful statement hashing."""
        # Mock the hash result
        mock_hash_result = StatementHashResult(
            statements=[123, 456],
            properties=["P1", "P2"],
            property_counts={"P1": 1, "P2": 1},
            full_statements=[
                {"mainsnak": {"property": "P1"}},
                {"mainsnak": {"property": "P2"}},
            ],
        )
        mock_hash.return_value = MagicMock(success=True, data=mock_hash_result)
        mock_store.return_value = MagicMock(success=True)

        entity_data = {"claims": {"P1": [{"mainsnak": {"property": "P1"}}]}}

        result = HashService.hash_statements(
            entity_data, self.mock_vitess, self.mock_s3, self.mock_validator
        )

        self.assertIsInstance(result, StatementsHashes)
        self.assertEqual(result.root, [123, 456])
        mock_hash.assert_called_once_with(entity_data)
        mock_store.assert_called_once()

    @patch("models.rest_api.v1.entitybase.services.hash_service.hash_entity_statements")
    def test_hash_statements_hash_failure(self, mock_hash) -> None:
        """Test statement hashing when hash operation fails."""
        mock_hash.return_value = MagicMock(success=False, error="Hash failed")

        with self.assertRaises(ValueError) as cm:
            HashService.hash_statements({}, self.mock_vitess, self.mock_s3)

        self.assertIn("Failed to hash statements", str(cm.exception))

    @patch(
        "models.rest_api.v1.entitybase.services.hash_service.deduplicate_and_store_statements"
    )
    @patch("models.rest_api.v1.entitybase.services.hash_service.hash_entity_statements")
    def test_hash_statements_store_failure(self, mock_hash, mock_store) -> None:
        """Test statement hashing when store operation fails."""
        mock_hash_result = StatementHashResult(
            statements=[123], properties=[], property_counts={}, full_statements=[]
        )
        mock_hash.return_value = MagicMock(success=True, data=mock_hash_result)
        mock_store.return_value = MagicMock(success=False, error="Store failed")

        with self.assertRaises(ValueError) as cm:
            HashService.hash_statements({}, self.mock_vitess, self.mock_s3)

        self.assertIn("Failed to store statements", str(cm.exception))

    @patch(
        "models.rest_api.v1.entitybase.services.hash_service.MetadataExtractor.hash_string"
    )
    @patch(
        "models.rest_api.v1.entitybase.services.hash_service.MyS3Client.store_sitelink_metadata"
    )
    def test_hash_sitelinks(self, mock_store, mock_hash) -> None:
        """Test sitelink hashing."""
        mock_hash.side_effect = [123, 456]

        sitelinks = {
            "enwiki": {"title": "Test Page"},
            "dewiki": {"title": "Test Seite"},
        }

        result = HashService.hash_sitelinks(sitelinks, self.mock_s3)

        self.assertIsInstance(result, SitelinksHashes)
        self.assertEqual(result.root, {"enwiki": 123, "dewiki": 456})
        self.assertEqual(mock_store.call_count, 2)
        mock_store.assert_any_call("Test Page", 123)
        mock_store.assert_any_call("Test Seite", 456)

    def test_hash_sitelinks_empty(self) -> None:
        """Test sitelink hashing with empty data."""
        result = HashService.hash_sitelinks({}, self.mock_s3)
        self.assertEqual(result.root, {})

    @patch(
        "models.rest_api.v1.entitybase.services.hash_service.MetadataExtractor.hash_string"
    )
    @patch("models.rest_api.v1.entitybase.services.hash_service.TermsRepository")
    @patch(
        "models.rest_api.v1.entitybase.services.hash_service.MyS3Client.store_term_metadata"
    )
    def test_hash_labels(self, mock_store, mock_repo_class, mock_hash) -> None:
        """Test label hashing."""
        mock_hash.side_effect = [123, 456]
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        labels = {"en": {"value": "Test Label"}, "de": {"value": "Test Etikett"}}

        result = HashService.hash_labels(labels, self.mock_s3, self.mock_vitess)

        self.assertIsInstance(result, LabelsHashes)
        self.assertEqual(result.root, {"en": 123, "de": 456})
        self.assertEqual(mock_store.call_count, 2)
        mock_repo.insert_term.assert_any_call(123, "Test Label", "label")
        mock_repo.insert_term.assert_any_call(456, "Test Etikett", "label")

    def test_hash_labels_empty(self) -> None:
        """Test label hashing with empty data."""
        result = HashService.hash_labels({}, self.mock_s3, self.mock_vitess)
        self.assertEqual(result.root, {})

    @patch(
        "models.rest_api.v1.entitybase.services.hash_service.MetadataExtractor.hash_string"
    )
    @patch("models.rest_api.v1.entitybase.services.hash_service.TermsRepository")
    @patch(
        "models.rest_api.v1.entitybase.services.hash_service.MyS3Client.store_term_metadata"
    )
    def test_hash_descriptions(self, mock_store, mock_repo_class, mock_hash) -> None:
        """Test description hashing."""
        mock_hash.side_effect = [123, 456]
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        descriptions = {
            "en": {"value": "Test Description"},
            "de": {"value": "Test Beschreibung"},
        }

        result = HashService.hash_descriptions(
            descriptions, self.mock_s3, self.mock_vitess
        )

        self.assertIsInstance(result, DescriptionsHashes)
        self.assertEqual(result.root, {"en": 123, "de": 456})
        mock_repo.insert_term.assert_any_call(123, "Test Description", "description")

    @patch(
        "models.rest_api.v1.entitybase.services.hash_service.MetadataExtractor.hash_string"
    )
    @patch("models.rest_api.v1.entitybase.services.hash_service.TermsRepository")
    @patch(
        "models.rest_api.v1.entitybase.services.hash_service.MyS3Client.store_term_metadata"
    )
    def test_hash_aliases(self, mock_store, mock_repo_class, mock_hash) -> None:
        """Test alias hashing."""
        mock_hash.side_effect = [123, 456, 789]
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        aliases = {
            "en": [{"value": "Test Alias"}, {"value": "Another Alias"}],
            "de": [{"value": "Test Alias DE"}],
        }

        result = HashService.hash_aliases(aliases, self.mock_s3, self.mock_vitess)

        self.assertIsInstance(result, AliasesHashes)
        self.assertEqual(result.root, {"en": [123, 456], "de": [789]})
        self.assertEqual(mock_store.call_count, 3)
        mock_repo.insert_term.assert_any_call(123, "Test Alias", "alias")

    def test_hash_aliases_empty(self) -> None:
        """Test alias hashing with empty data."""
        result = HashService.hash_aliases({}, self.mock_s3, self.mock_vitess)
        self.assertEqual(result.root, {})

    @patch.object(HashService, "hash_statements")
    @patch.object(HashService, "hash_sitelinks")
    @patch.object(HashService, "hash_labels")
    @patch.object(HashService, "hash_descriptions")
    @patch.object(HashService, "hash_aliases")
    def test_hash_entity_metadata(
        self, mock_aliases, mock_desc, mock_labels, mock_sitelinks, mock_statements
    ):
        """Test combined entity metadata hashing."""
        mock_statements.return_value = StatementsHashes(root=[123])
        mock_sitelinks.return_value = SitelinksHashes(root={"enwiki": 456})
        mock_labels.return_value = LabelsHashes(root={"en": 789})
        mock_desc.return_value = DescriptionsHashes(root={"en": 101})
        mock_aliases.return_value = AliasesHashes(root={"en": [112]})

        entity_data = {
            "claims": {},
            "sitelinks": {},
            "labels": {},
            "descriptions": {},
            "aliases": {},
        }

        result = HashService.hash_entity_metadata(
            entity_data, self.mock_vitess, self.mock_s3, self.mock_validator
        )

        self.assertIsInstance(result, HashMaps)
        self.assertEqual(result.statements.root, [123])
        self.assertEqual(result.sitelinks.root, {"enwiki": 456})
        self.assertEqual(result.labels.root, {"en": 789})
        self.assertEqual(result.descriptions.root, {"en": 101})
        self.assertEqual(result.aliases.root, {"en": [112]})

        mock_statements.assert_called_once_with(
            entity_data, self.mock_vitess, self.mock_s3, self.mock_validator
        )
        mock_sitelinks.assert_called_once_with({}, self.mock_s3)
        mock_labels.assert_called_once_with({}, self.mock_s3, self.mock_vitess)
        mock_desc.assert_called_once_with({}, self.mock_s3, self.mock_vitess)
        mock_aliases.assert_called_once_with({}, self.mock_s3, self.mock_vitess)


if __name__ == "__main__":
    unittest.main()
