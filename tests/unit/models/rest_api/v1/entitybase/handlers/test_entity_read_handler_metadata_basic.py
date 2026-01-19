import unittest
from unittest.mock import Mock, patch
from models.rest_api.v1.entitybase.handlers.entity.read import EntityReadHandler


class TestEntityReadHandlerMetadataBasic(unittest.TestCase):
    """Unit tests for EntityReadHandler basic metadata methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = EntityReadHandler()
        self.mock_vitess = Mock()
        self.mock_s3 = Mock()

    @patch("models.rest_api.v1.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.infrastructure.vitess.repositories.terms.TermsRepository")
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

    @patch("models.rest_api.v1.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.infrastructure.vitess.repositories.terms.TermsRepository")
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

    @patch("models.rest_api.v1.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.infrastructure.vitess.repositories.terms.TermsRepository")
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

    @patch("models.rest_api.v1.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.infrastructure.vitess.repositories.terms.TermsRepository")
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
        self.assertIn("entity", entity_data)
        self.assertIn("labels", entity_data["entity"])

    @patch("models.rest_api.v1.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.infrastructure.vitess.repositories.terms.TermsRepository")
    def test_get_entity_legacy_labels_none(
        self, mock_terms_repo_class, mock_entity_response
    ):
        """Test legacy get_entity with labels where get_term returns None"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {
            "entity": {"id": "Q42"},
            "labels_hashes": {"en": "hash1"},
            "descriptions_hashes": {},
            "aliases_hashes": {},
        }
        self.mock_s3.read_revision.return_value = mock_revision

        mock_terms_repo = Mock()
        mock_terms_repo.get_term.return_value = None  # None for labels
        mock_terms_repo_class.return_value = mock_terms_repo

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=False
        )

        self.assertEqual(result, mock_response_instance)
        # Check that labels dict is not added
        call_args = mock_entity_response.call_args
        entity_data = call_args[1]["entity_data"]
        self.assertNotIn("labels", entity_data["entity"])

    @patch("models.rest_api.v1.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.infrastructure.vitess.repositories.terms.TermsRepository")
    def test_get_entity_legacy_aliases_partial_none(
        self, mock_terms_repo_class, mock_entity_response
    ):
        """Test legacy get_entity with aliases where some get_term returns None"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {
            "entity": {"id": "Q42"},
            "labels_hashes": {},
            "descriptions_hashes": {},
            "aliases_hashes": {"en": ["hash1", "hash2"]},
        }
        self.mock_s3.read_revision.return_value = mock_revision

        mock_terms_repo = Mock()
        mock_terms_repo.get_term.side_effect = (
            lambda h: "Alias1" if h == "hash1" else None
        )
        mock_terms_repo_class.return_value = mock_terms_repo

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=False
        )

        self.assertEqual(result, mock_response_instance)
        # Check that only non-None aliases are included
        call_args = mock_entity_response.call_args
        entity_data = call_args[1]["entity_data"]
        self.assertIn("aliases", entity_data["entity"])
        self.assertEqual(len(entity_data["entity"]["aliases"]["en"]), 1)
        self.assertEqual(entity_data["entity"]["aliases"]["en"][0]["value"], "Alias1")

    @patch("models.rest_api.v1.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.infrastructure.vitess.repositories.terms.TermsRepository")
    def test_get_entity_legacy_descriptions(
        self, mock_terms_repo_class, mock_entity_response
    ):
        """Test legacy get_entity with descriptions"""
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
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=False
        )

        self.assertEqual(result, mock_response_instance)
        # Check descriptions are loaded
        call_args = mock_entity_response.call_args
        entity_data = call_args[1]["entity_data"]
        self.assertIn("descriptions", entity_data["entity"])
        self.assertEqual(
            entity_data["entity"]["descriptions"]["en"]["value"], "Description EN"
        )

    @patch("models.rest_api.v1.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.infrastructure.vitess.repositories.terms.TermsRepository")
    def test_get_entity_success_all_metadata_types(
        self, mock_terms_repo_class, mock_entity_response
    ):
        """Test get_entity success with all metadata types loaded"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {
            "entity": {"id": "Q42"},
            "labels_hashes": {"en": "hash_label_en", "fr": "hash_label_fr"},
            "descriptions_hashes": {"en": "hash_desc_en", "de": "hash_desc_de"},
            "aliases_hashes": {
                "en": ["hash_alias_en1", "hash_alias_en2"],
                "es": ["hash_alias_es"],
            },
        }
        self.mock_s3.read_revision.return_value = mock_revision

        mock_terms_repo = Mock()

        def mock_get_term(hash_val):
            terms = {
                "hash_label_en": "Label EN",
                "hash_label_fr": "Label FR",
                "hash_alias_en1": "Alias EN1",
                "hash_alias_en2": "Alias EN2",
                "hash_alias_es": "Alias ES",
            }
            return terms.get(hash_val)

        mock_terms_repo.get_term.side_effect = mock_get_term
        mock_terms_repo_class.return_value = mock_terms_repo

        def mock_load_metadata(key, hash_val):
            metadata = {
                ("descriptions", "hash_desc_en"): "Description EN",
                ("descriptions", "hash_desc_de"): "Description DE",
            }
            return metadata.get((key, hash_val), {})

        self.mock_s3.load_metadata.side_effect = mock_load_metadata

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=True
        )

        self.assertEqual(result, mock_response_instance)
        # Check all metadata types are loaded
        call_args = mock_entity_response.call_args
        entity_data = call_args[1]["entity_data"]
        self.assertIn("labels", entity_data)
        self.assertEqual(len(entity_data["labels"]), 2)
        self.assertIn("descriptions", entity_data)
        self.assertEqual(len(entity_data["descriptions"]), 2)
        self.assertIn("aliases", entity_data)
        self.assertEqual(len(entity_data["aliases"]["en"]), 2)
        self.assertEqual(len(entity_data["aliases"]["es"]), 1)


if __name__ == "__main__":
    unittest.main()
