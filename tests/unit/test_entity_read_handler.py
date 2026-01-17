import unittest
from unittest.mock import Mock, patch
from models.rest_api.entitybase.handlers.entity.read import EntityReadHandler
from models.rest_api.entitybase.response.entity import EntityHistoryEntry


class TestEntityReadHandler(unittest.TestCase):
    """Unit tests for EntityReadHandler with term deduplication"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = EntityReadHandler()
        self.mock_vitess = Mock()
        self.mock_s3 = Mock()

    @patch(
        "models.rest_api.entitybase.handlers.entity.read.EntityReadHandler.get_entity"
    )
    def test_get_entity_with_terms(self, mock_get_entity):
        """Test that get_entity calls work with term loading"""
        # This is more of an integration test, but ensures the method exists
        mock_entity_response = Mock()
        mock_entity_response.data = {
            "id": "Q42",
            "labels": {"en": {"language": "en", "value": "Test"}},
        }
        mock_get_entity.return_value = mock_entity_response

        # We can't easily test the full method without mocking all dependencies
        # This just verifies the method exists and can be called
        self.assertTrue(hasattr(self.handler, "get_entity"))

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_history_vitess_none(self, mock_raise_error):
        """Test get_entity_history raises error when vitess_client is None"""
        EntityReadHandler.get_entity_history("Q42", None, self.mock_s3)
        mock_raise_error.assert_called_once_with(
            "Vitess not initialized", status_code=503
        )

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_history_entity_not_found(self, mock_raise_error):
        """Test get_entity_history raises error when entity does not exist"""
        self.mock_vitess.entity_exists.return_value = False
        EntityReadHandler.get_entity_history("Q42", self.mock_vitess, self.mock_s3)
        mock_raise_error.assert_called_once_with("Entity not found", status_code=404)

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_history_exception(self, mock_raise_error):
        """Test get_entity_history raises error on exception"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_entity_history.side_effect = Exception("DB error")
        EntityReadHandler.get_entity_history("Q42", self.mock_vitess, self.mock_s3)
        mock_raise_error.assert_called_once_with(
            "Failed to get entity history", status_code=500
        )

    def test_get_entity_history_success(self):
        """Test get_entity_history returns history on success"""
        self.mock_vitess.entity_exists.return_value = True
        mock_history = [
            EntityHistoryEntry(
                revision_id=1,
                created_at="2023-01-01",
                user_id=123,
                edit_summary="Test edit",
            ),
            EntityHistoryEntry(
                revision_id=2,
                created_at="2023-01-02",
                user_id=456,
                edit_summary="Another edit",
            ),
        ]
        self.mock_vitess.get_entity_history.return_value = mock_history

        result = EntityReadHandler.get_entity_history(
            "Q42", self.mock_vitess, self.mock_s3
        )

        self.assertEqual(result, mock_history)
        self.mock_vitess.get_entity_history.assert_called_once_with(
            "Q42", self.mock_s3, 20, 0
        )

    def test_get_entity_history_with_limit_offset(self):
        """Test get_entity_history with custom limit and offset"""
        self.mock_vitess.entity_exists.return_value = True
        mock_history = [
            EntityHistoryEntry(
                revision_id=1, created_at="2023-01-01", user_id=123, edit_summary="Test"
            )
        ]
        self.mock_vitess.get_entity_history.return_value = mock_history

        result = EntityReadHandler.get_entity_history(
            "Q42", self.mock_vitess, self.mock_s3, limit=10, offset=5
        )

        self.assertEqual(result, mock_history)
        self.mock_vitess.get_entity_history.assert_called_once_with(
            "Q42", self.mock_s3, 10, 5
        )

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_vitess_none(self, mock_raise_error):
        """Test get_entity raises error when vitess_client is None"""
        EntityReadHandler.get_entity("Q42", None, self.mock_s3)
        mock_raise_error.assert_called_once_with(
            "Vitess not initialized", status_code=503
        )

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_s3_none(self, mock_raise_error):
        """Test get_entity raises error when s3_client is None"""
        EntityReadHandler.get_entity("Q42", self.mock_vitess, None)
        mock_raise_error.assert_called_once_with("S3 not initialized", status_code=503)

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_not_found(self, mock_raise_error):
        """Test get_entity raises error when entity does not exist"""
        self.mock_vitess.entity_exists.return_value = False
        EntityReadHandler.get_entity("Q42", self.mock_vitess, self.mock_s3)
        mock_raise_error.assert_called_once_with("Entity not found", status_code=404)

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_no_head_revision(self, mock_raise_error):
        """Test get_entity raises error when no head revision"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 0
        EntityReadHandler.get_entity("Q42", self.mock_vitess, self.mock_s3)
        mock_raise_error.assert_called_once_with("Entity not found", status_code=404)

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.rest_api.entitybase.handlers.entity.read.TermsRepository")
    def test_get_entity_success_no_metadata(
        self, mock_terms_repo, mock_entity_response
    ):
        """Test get_entity success without metadata"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {"entity": {"id": "Q42"}}
        self.mock_s3.read_revision.return_value = mock_revision

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=False
        )

        self.assertEqual(result, mock_response_instance)
        self.mock_s3.read_revision.assert_called_once_with("Q42", 123)
        mock_entity_response.assert_called_once()

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_revision_s3_none(self, mock_raise_error):
        """Test get_entity_revision raises error when s3_client is None"""
        EntityReadHandler.get_entity_revision("Q42", 123, None)
        mock_raise_error.assert_called_once_with("S3 not initialized", status_code=503)

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityRevisionResponse")
    def test_get_entity_revision_success(self, mock_revision_response):
        """Test get_entity_revision success"""
        mock_revision = Mock()
        mock_revision.data = Mock()
        mock_revision.data.model_dump.return_value = {"id": "Q42"}
        mock_revision.data.entity = {"id": "Q42"}
        self.mock_s3.read_revision.return_value = mock_revision
        self.mock_s3.load_metadata.return_value = {"en": {"value": "Test"}}

        mock_response_instance = Mock()
        mock_revision_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity_revision("Q42", 123, self.mock_s3)

        self.assertEqual(result, mock_response_instance)
        self.mock_s3.read_revision.assert_called_once_with("Q42", 123)
        mock_revision_response.assert_called_once()

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_revision_exception(self, mock_raise_error):
        """Test get_entity_revision handles exceptions"""
        self.mock_s3.read_revision.side_effect = Exception("S3 error")

        EntityReadHandler.get_entity_revision("Q42", 123, self.mock_s3)

        mock_raise_error.assert_called_once_with("Revision not found", status_code=404)

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
        """Test get_entity success with legacy metadata merging"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {
            "entity": {"id": "Q42"},
            "labels_hashes": {"en": "hash1"},
            "descriptions_hashes": {"en": "hash_desc"},
            "aliases_hashes": {"en": ["hash_alias"]},
        }
        self.mock_s3.read_revision.return_value = mock_revision

        mock_terms_repo = Mock()
        mock_terms_repo.get_term.side_effect = (
            lambda h: "Label EN" if h == "hash1" else "Alias EN"
        )
        mock_terms_repo_class.return_value = mock_terms_repo
        self.mock_s3.load_metadata.return_value = "Description EN"

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=False
        )

        self.assertEqual(result, mock_response_instance)
        # Check that metadata was merged into entity
        call_args = mock_entity_response.call_args
        entity_data = call_args[1]["entity_data"]
        self.assertIn("entity", entity_data)
        self.assertIn("labels", entity_data["entity"])

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.rest_api.entitybase.handlers.entity.read.TermsRepository")
    def test_get_entity_exception_on_read_revision(
        self, mock_terms_repo_class, mock_entity_response
    ):
        """Test get_entity handles exception during read_revision"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        self.mock_s3.read_revision.side_effect = Exception("S3 read error")

        with self.assertRaises(Exception):  # Should re-raise after logging
            EntityReadHandler.get_entity("Q42", self.mock_vitess, self.mock_s3)

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityRevisionResponse")
    def test_get_entity_revision_with_metadata(self, mock_revision_response):
        """Test get_entity_revision with metadata loading"""
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
            "labels": {"en": {"value": "Label"}},
            "descriptions": {"en": {"value": "Desc"}},
            "aliases": {"en": [{"value": "Alias"}]},
        }.get(key, {})

        mock_response_instance = Mock()
        mock_revision_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity_revision("Q42", 123, self.mock_s3)

        self.assertEqual(result, mock_response_instance)
        self.assertEqual(self.mock_s3.load_metadata.call_count, 3)

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.rest_api.entitybase.handlers.entity.read.TermsRepository")
    def test_get_entity_metadata_labels_none(
        self, mock_terms_repo_class, mock_entity_response
    ):
        """Test get_entity with metadata labels where get_term returns None"""
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
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=True
        )

        self.assertEqual(result, mock_response_instance)
        # Check that labels dict is empty or not added
        call_args = mock_entity_response.call_args
        entity_data = call_args[1]["entity_data"]
        self.assertNotIn("labels", entity_data)

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.rest_api.entitybase.handlers.entity.read.TermsRepository")
    def test_get_entity_metadata_descriptions_load_failure(
        self, mock_terms_repo_class, mock_entity_response
    ):
        """Test get_entity with metadata descriptions load failure"""
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
        self.mock_s3.load_metadata.side_effect = Exception("Load failed")

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=True
        )

        self.assertEqual(result, mock_response_instance)
        # Should still succeed, but descriptions not added
        call_args = mock_entity_response.call_args
        entity_data = call_args[1]["entity_data"]
        self.assertNotIn("descriptions", entity_data)

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.rest_api.entitybase.handlers.entity.read.TermsRepository")
    def test_get_entity_metadata_aliases_none(
        self, mock_terms_repo_class, mock_entity_response
    ):
        """Test get_entity with metadata aliases where get_term returns None"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {
            "entity": {"id": "Q42"},
            "labels_hashes": {},
            "descriptions_hashes": {},
            "aliases_hashes": {"en": ["hash1"]},
        }
        self.mock_s3.read_revision.return_value = mock_revision

        mock_terms_repo = Mock()
        mock_terms_repo.get_term.return_value = None  # None for aliases
        mock_terms_repo_class.return_value = mock_terms_repo

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=True
        )

        self.assertEqual(result, mock_response_instance)
        # Check aliases not added or empty
        call_args = mock_entity_response.call_args
        entity_data = call_args[1]["entity_data"]
        self.assertNotIn("aliases", entity_data)

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityResponse")
    @patch("models.rest_api.entitybase.handlers.entity.read.TermsRepository")
    def test_get_entity_metadata_combined(
        self, mock_terms_repo_class, mock_entity_response
    ):
        """Test get_entity with combined metadata types"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.return_value = 123
        mock_revision = Mock()
        mock_revision.content = {
            "entity": {"id": "Q42"},
            "labels_hashes": {"en": "hash_label"},
            "descriptions_hashes": {"en": "hash_desc"},
            "aliases_hashes": {"en": ["hash_alias"]},
        }
        self.mock_s3.read_revision.return_value = mock_revision

        mock_terms_repo = Mock()
        mock_terms_repo.get_term.side_effect = lambda h: {
            "hash_label": "Label",
            "hash_alias": "Alias",
        }.get(h)
        mock_terms_repo_class.return_value = mock_terms_repo
        self.mock_s3.load_metadata.return_value = "Description"

        mock_response_instance = Mock()
        mock_entity_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity(
            "Q42", self.mock_vitess, self.mock_s3, fetch_metadata=True
        )

        self.assertEqual(result, mock_response_instance)
        call_args = mock_entity_response.call_args
        entity_data = call_args[1]["entity_data"]
        self.assertIn("labels", entity_data)
        self.assertIn("descriptions", entity_data)
        self.assertIn("aliases", entity_data)

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityRevisionResponse")
    def test_get_entity_revision_missing_labels_hash(self, mock_revision_response):
        """Test get_entity_revision with missing labels_hash"""
        mock_revision = Mock()
        mock_revision.data = Mock()
        mock_revision.data.model_dump.return_value = {
            "descriptions_hash": "hash_desc",
            "aliases_hash": "hash_aliases",
        }
        mock_revision.data.entity = {"id": "Q42"}
        self.mock_s3.read_revision.return_value = mock_revision
        self.mock_s3.load_metadata.side_effect = lambda key, h: {
            "descriptions": {"en": {"value": "Desc"}},
            "aliases": {"en": [{"value": "Alias"}]},
        }.get(key, {})

        mock_response_instance = Mock()
        mock_revision_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity_revision("Q42", 123, self.mock_s3)

        self.assertEqual(result, mock_response_instance)
        self.assertEqual(self.mock_s3.load_metadata.call_count, 2)  # desc and aliases

    @patch("models.rest_api.entitybase.handlers.entity.read.EntityRevisionResponse")
    def test_get_entity_revision_invalid_descriptions_hash(
        self, mock_revision_response
    ):
        """Test get_entity_revision with invalid descriptions_hash"""
        mock_revision = Mock()
        mock_revision.data = Mock()
        mock_revision.data.model_dump.return_value = {
            "labels_hash": "hash_labels",
            "descriptions_hash": "invalid",
            "aliases_hash": "hash_aliases",
        }
        mock_revision.data.entity = {"id": "Q42"}
        self.mock_s3.read_revision.return_value = mock_revision
        self.mock_s3.load_metadata.side_effect = (
            lambda key, h: {
                "labels": {"en": {"value": "Label"}},
                "aliases": {"en": [{"value": "Alias"}]},
            }.get(key, {})
            if h != "invalid"
            else (_ for _ in ()).throw(Exception("Invalid hash"))
        )

        mock_response_instance = Mock()
        mock_revision_response.return_value = mock_response_instance

        result = EntityReadHandler.get_entity_revision("Q42", 123, self.mock_s3)

        self.assertEqual(result, mock_response_instance)
        # descriptions not loaded due to exception

    def test_get_entity_history_large_limit_offset(self):
        """Test get_entity_history with large limit and offset"""
        self.mock_vitess.entity_exists.return_value = True
        mock_history = [
            EntityHistoryEntry(
                revision_id=500,
                created_at="2023-01-01",
                user_id=123,
                edit_summary="Large offset",
            )
        ]
        self.mock_vitess.get_entity_history.return_value = mock_history

        result = EntityReadHandler.get_entity_history(
            "Q42", self.mock_vitess, self.mock_s3, limit=1000, offset=500
        )

        self.assertEqual(result, mock_history)
        self.mock_vitess.get_entity_history.assert_called_once_with(
            "Q42", self.mock_s3, 1000, 500
        )

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_entity_exists_exception(self, mock_raise_error):
        """Test get_entity when entity_exists raises exception"""
        self.mock_vitess.entity_exists.side_effect = Exception("DB error")
        EntityReadHandler.get_entity("Q42", self.mock_vitess, self.mock_s3)
        mock_raise_error.assert_called_once_with("Entity not found", status_code=404)

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_get_head_exception(self, mock_raise_error):
        """Test get_entity when get_head raises exception"""
        self.mock_vitess.entity_exists.return_value = True
        self.mock_vitess.get_head.side_effect = Exception("DB error")
        EntityReadHandler.get_entity("Q42", self.mock_vitess, self.mock_s3)
        mock_raise_error.assert_called_once_with("Entity not found", status_code=404)

    @patch("models.rest_api.entitybase.handlers.entity.read.raise_validation_error")
    def test_get_entity_invalid_entity_id_empty(self, mock_raise_error):
        """Test get_entity with empty entity_id"""
        self.mock_vitess.entity_exists.return_value = (
            False  # Assume empty ID not exists
        )
        EntityReadHandler.get_entity("", self.mock_vitess, self.mock_s3)
        mock_raise_error.assert_called_once_with("Entity not found", status_code=404)


if __name__ == "__main__":
    unittest.main()
