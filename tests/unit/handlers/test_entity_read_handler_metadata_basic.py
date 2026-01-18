import unittest
from unittest.mock import Mock, patch
from models.rest_api.entitybase.handlers.entity.read import EntityReadHandler


class TestEntityReadHandlerMetadataBasic(unittest.TestCase):
    """Unit tests for EntityReadHandler basic metadata methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = EntityReadHandler()
        self.mock_vitess = Mock()
        self.mock_s3 = Mock()

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.rest_api.entitybase.handlers.entity.read.TermsRepository")
    def test_get_entity_success_with_metadata_labels(
        self, mock_terms_repo_class, mock_entity_response
    ):
        """Test get_entity success with metadata labels loaded"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {
            "entity": {"id": "Q42"},
            "labels_hashes": {"en": "hash1", "fr": "hash2"},
            "descriptions_hashes": {},
            "aliases_hashes": {},
        }
        self.mock_s3.read_revision.return_value = mock_revision

        mock_terms_repo = Mock()
        mock_terms_repo.get_term.side_effect = (
            lambda h: "Label EN" if h == "hash1" else "Label FR"
        )
        mock_terms_repo_class.return_value = mock_terms_repo

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=True
        )

        self.assertEqual(result, mock_response_instance)
        # Check that labels were added to data
        call_args = mock_entity_response.call_args
        entity_data = call_args[1]["entity_data"]
        self.assertIn("labels", entity_data)
        self.assertEqual(entity_data["labels"]["en"]["value"], "Label EN")

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.rest_api.entitybase.handlers.entity.read.TermsRepository")
    def test_get_entity_success_with_metadata_descriptions(
        self, mock_terms_repo_class, mock_entity_response
    ):
        """Test get_entity success with metadata descriptions loaded"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {
            "entity": {"id": "Q42"},
            "labels_hashes": {},
            "descriptions_hashes": {"en": "hash_desc"},
            "aliases_hashes": {},
        }
        self.mock_s3.read_revision.return_value = mock_revision

        mock_terms_repo = Mock()
        mock_terms_repo_class.return_value = mock_terms_repo
        self.mock_s3.load_metadata.return_value = "Description EN"

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=True
        )

        self.assertEqual(result, mock_response_instance)
        self.mock_s3.load_metadata.assert_called_with("descriptions", "hash_desc")

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.rest_api.entitybase.handlers.entity.read.TermsRepository")
    def test_get_entity_success_with_metadata_aliases(
        self, mock_terms_repo_class, mock_entity_response
    ):
        """Test get_entity success with metadata aliases loaded"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {
            "entity": {"id": "Q42"},
            "labels_hashes": {},
            "descriptions_hashes": {},
            "aliases_hashes": {"en": ["hash_alias1", "hash_alias2"]},
        }
        self.mock_s3.read_revision.return_value = mock_revision

        mock_terms_repo = Mock()
        mock_terms_repo.get_term.side_effect = (
            lambda h: "Alias 1" if h == "hash_alias1" else "Alias 2"
        )
        mock_terms_repo_class.return_value = mock_terms_repo

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=True
        )

        self.assertEqual(result, mock_response_instance)
        # Check aliases in data
        call_args = mock_entity_response.call_args
        entity_data = call_args[1]["entity_data"]
        self.assertIn("aliases", entity_data)
        self.assertEqual(len(entity_data["aliases"]["en"]), 2)

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.rest_api.entitybase.handlers.entity.read.TermsRepository")
    def test_get_entity_success_legacy_metadata(
        self, mock_terms_repo_class, mock_entity_response
    ):
        """Test get_entity success with legacy metadata format"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {
            "entity": {"id": "Q42"},
            "labels_hashes": {},
            "descriptions_hashes": {},
            "aliases_hashes": {},
            "metadata": {
                "labels": {"en": {"language": "en", "value": "Test Label"}},
                "descriptions": {"en": {"language": "en", "value": "Test Description"}},
                "aliases": {"en": [{"language": "en", "value": "Test Alias"}]},
            },
        }
        self.mock_s3.read_revision.return_value = mock_revision

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=True
        )

        self.assertEqual(result, mock_response_instance)
        # Check legacy metadata was used
        call_args = mock_entity_response.call_args
        entity_data = call_args[1]["entity_data"]
        self.assertIn("labels", entity_data)
        self.assertEqual(entity_data["labels"]["en"]["value"], "Test Label")


if __name__ == "__main__":
    unittest.main()