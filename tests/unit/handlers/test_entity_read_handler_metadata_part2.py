import unittest
from unittest.mock import Mock, patch
from models.rest_api.entitybase.handlers.entity.read import EntityReadHandler


class TestEntityReadHandlerMetadataPart2(unittest.TestCase):
    """Unit tests for EntityReadHandler metadata methods - Part 2"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = EntityReadHandler()
        self.mock_vitess = Mock()
        self.mock_s3 = Mock()

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.rest_api.entitybase.handlers.entity.read.TermsRepository")
    def test_get_entity_metadata_aliases_load_failure(
        self, mock_terms_repo_class, mock_entity_response
    ):
        """Test get_entity with metadata aliases load failure"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {
            "entity": {"id": "Q42"},
            "labels_hashes": {},
            "descriptions_hashes": {},
            "aliases_hashes": {"en": ["hash_alias"]},
        }
        self.mock_s3.read_revision.return_value = mock_revision
        self.mock_s3.load_metadata.side_effect = Exception("Load failed")

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=True
        )

        self.assertEqual(result, mock_response_instance)
        call_args = mock_entity_response.call_args
        entity_data = call_args[1]["entity_data"]
        self.assertNotIn("aliases", entity_data)

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.rest_api.entitybase.handlers.entity.read.TermsRepository")
    def test_get_entity_partial_metadata_none_terms(
        self, mock_terms_repo_class, mock_entity_response
    ):
        """Test get_entity with partial metadata where some terms return None"""
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
            lambda h: "Label EN" if h == "hash1" else None
        )
        mock_terms_repo_class.return_value = mock_terms_repo

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=True
        )

        self.assertEqual(result, mock_response_instance)
        call_args = mock_entity_response.call_args
        entity_data = call_args[1]["entity_data"]
        self.assertIn("labels", entity_data)
        self.assertIn("en", entity_data["labels"])
        self.assertNotIn("fr", entity_data["labels"])  # None term not included

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    def test_get_entity_legacy_empty_hashes(self, mock_entity_response):
        """Test get_entity legacy path with empty hashes dicts"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {
            "entity": {"id": "Q42"},
            "labels_hashes": {},
            "descriptions_hashes": {},
            "aliases_hashes": {},
        }
        self.mock_s3.read_revision.return_value = mock_revision

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=False
        )

        self.assertEqual(result, mock_response_instance)
        # Should not attempt metadata loading

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.rest_api.entitybase.handlers.entity.read.TermsRepository")
    def test_get_entity_mixed_metadata_types(
        self, mock_terms_repo_class, mock_entity_response
    ):
        """Test get_entity with mixed present/missing metadata types"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {
            "entity": {"id": "Q42"},
            "labels_hashes": {"en": "hash_label"},
            "descriptions_hashes": {},  # empty
            "aliases_hashes": {"en": ["hash_alias"]},  # present
        }
        self.mock_s3.read_revision.return_value = mock_revision

        mock_terms_repo = Mock()
        mock_terms_repo.get_term.side_effect = lambda h: {
            "hash_label": "Label",
            "hash_alias": "Alias",
        }.get(h)
        mock_terms_repo_class.return_value = mock_terms_repo

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=True
        )

        self.assertEqual(result, mock_response_instance)
        call_args = mock_entity_response.call_args
        entity_data = call_args[1]["entity_data"]
        self.assertIn("labels", entity_data)
        self.assertNotIn("descriptions", entity_data)  # empty dict skipped
        self.assertIn("aliases", entity_data)

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityRevisionResponse")
    def test_get_entity_revision_s3_load_labels_failure(self, mock_revision_response):
        """Test get_entity_revision with S3 load failure for labels"""
        mock_revision = Mock()
        mock_revision.data = Mock()
        mock_revision.data.model_dump.return_value = {
            "labels_hash": "hash_labels",
            "descriptions_hash": "hash_desc",
            "aliases_hash": "hash_aliases",
        }
        mock_revision.data.entity = {"id": "Q42"}
        self.mock_s3.read_revision.return_value = mock_revision
        self.mock_s3.load_metadata.side_effect = lambda key, h: {
            "labels": Exception("Load failed"),
            "descriptions": {"en": {"value": "Desc"}},
            "aliases": {"en": [{"value": "Alias"}]},
        }.get(key, {})

        mock_response_instance = Mock()
        mock_revision_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity_revision("Q42", 123, self.mock_s3)

        self.assertEqual(result, mock_response_instance)
        # Should not include labels in response due to failure

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityRevisionResponse")
    def test_get_entity_revision_missing_hash_keys(self, mock_revision_response):
        """Test get_entity_revision with missing hash keys in revision data"""
        mock_revision = Mock()
        mock_revision.data = Mock()
        mock_revision.data.model_dump.return_value = {
            # missing labels_hash, descriptions_hash, aliases_hash
        }
        mock_revision.data.entity = {"id": "Q42"}
        self.mock_s3.read_revision.return_value = mock_revision
        self.mock_s3.load_metadata.side_effect = lambda key, h: {}  # not called

        mock_response_instance = Mock()
        mock_revision_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity_revision("Q42", 123, self.mock_s3)

        self.assertEqual(result, mock_response_instance)
        self.assertEqual(self.mock_s3.load_metadata.call_count, 0)  # no hashes

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityRevisionResponse")
    def test_get_entity_revision_invalid_hash_keys(self, mock_revision_response):
        """Test get_entity_revision with invalid hash keys"""
        mock_revision = Mock()
        mock_revision.data = Mock()
        mock_revision.data.model_dump.return_value = {
            "labels_hash": None,  # invalid
            "descriptions_hash": "",
            "aliases_hash": [],
        }
        mock_revision.data.entity = {"id": "Q42"}
        self.mock_s3.read_revision.return_value = mock_revision
        self.mock_s3.load_metadata.side_effect = (
            lambda key, h: {}
        )  # not called for invalid

        mock_response_instance = Mock()
        mock_revision_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity_revision("Q42", 123, self.mock_s3)

        self.assertEqual(result, mock_response_instance)
        self.assertEqual(
            self.mock_s3.load_metadata.call_count, 0
        )  # invalid hashes not loaded

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    def test_get_entity_revision_content_missing_entity_key(self, mock_entity_response):
        """Test get_entity_revision with revision.content missing 'entity' key"""
        mock_revision = Mock()
        mock_revision.content = {
            # missing "entity" key
            "labels_hashes": {},
            "descriptions_hashes": {},
            "aliases_hashes": {},
        }
        self.mock_s3.read_revision.return_value = mock_revision

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity_revision("Q42", 123, self.mock_s3)

        self.assertEqual(result, mock_response_instance)
        # Should handle missing entity key

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    def test_get_entity_invalid_hash_structures(self, mock_entity_response):
        """Test get_entity with invalid hash structures"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {
            "entity": {"id": "Q42"},
            "labels_hashes": "invalid_string",  # should be dict
            "descriptions_hashes": None,
            "aliases_hashes": [],
        }
        self.mock_s3.read_revision.return_value = mock_revision

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=True
        )

        self.assertEqual(result, mock_response_instance)
        # Should handle invalid structures

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    def test_get_entity_empty_metadata_dicts(self, mock_entity_response):
        """Test get_entity with empty metadata dicts"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {
            "entity": {"id": "Q42"},
            "labels_hashes": {},
            "descriptions_hashes": {},
            "aliases_hashes": {},
        }
        self.mock_s3.read_revision.return_value = mock_revision

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=True
        )

        self.assertEqual(result, mock_response_instance)
        # Should not load metadata for empty dicts

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_exception(self, mock_raise_error):
        """Test get_entity handles exceptions during processing."""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        self.mock_s3.read_revision.side_effect = Exception("Read error")

        EntityReadHandler.get_entity("Q42", self.mock_vitess, self.mock_s3)

        mock_raise_error.assert_called_once_with(
            "Failed to read entity", status_code=500
        )

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    @patch("models.rest_api.entitybase.handlers.entity.read.isinstance")
    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.rest_api.entitybase.handlers.entity.read.TermsRepository")
    def test_get_entity_invalid_response_type(
        self, mock_terms_repo, mock_entity_response, mock_isinstance, mock_raise_error
    ):
        """Test get_entity raises error for invalid response type."""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {"entity": {"id": "Q42"}}
        self.mock_s3.read_revision.return_value = mock_revision

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance
        mock_isinstance.return_value = False  # Simulate invalid type

        EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=False
        )

        mock_raise_error.assert_called_once_with(
            "Invalid response type", status_code=500
        )

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_revision_invalid_revision_id_zero(self, mock_raise_error):
        """Test get_entity_revision with revision_id <= 0."""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 10

        EntityReadHandler.get_entity_revision("Q42", 0, self.mock_s3)

        mock_raise_error.assert_called_once_with("Invalid revision ID", status_code=400)

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_revision_invalid_revision_id_negative(self, mock_raise_error):
        """Test get_entity_revision with negative revision_id."""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 10

        EntityReadHandler.get_entity_revision("Q42", -1, self.mock_s3)

        mock_raise_error.assert_called_once_with("Invalid revision ID", status_code=400)

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_revision_revision_too_high(self, mock_raise_error):
        """Test get_entity_revision with revision_id > head."""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 10

        EntityReadHandler.get_entity_revision("Q42", 11, self.mock_s3)

        mock_raise_error.assert_called_once_with(
            "Revision 11 not found for entity Q42", status_code=404
        )


if __name__ == "__main__":
    unittest.main()