"""Unit tests for S3 client."""

from unittest.mock import MagicMock, patch

import pytest

from models.infrastructure.s3.client import MyS3Client


class TestMyS3Client:
    """Unit tests for MyS3Client."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = MagicMock()
        self.client = MyS3Client.__new__(MyS3Client)
        self.client.config = self.config
        self.client.connection_manager = MagicMock()
        self.client.revisions = MagicMock()
        self.client.statements = MagicMock()
        self.client.metadata = MagicMock()
        self.client.references = MagicMock()
        self.client.qualifiers = MagicMock()
        self.client.snaks = MagicMock()

    def test_mark_published(self):
        """Test mark_published method."""
        self.client.mark_published("Q42", 123, "published")

        self.client.revisions.mark_published.assert_called_once_with("Q42", 123, "published")

    def test_delete_statement(self):
        """Test delete_statement method."""
        self.client.statements.delete_statement.return_value = MagicMock(success=True)

        self.client.delete_statement(12345)

        self.client.statements.delete_statement.assert_called_once_with(12345)

    def test_delete_statement_failure(self):
        """Test delete_statement when storage fails."""
        self.client.statements.delete_statement.return_value = MagicMock(success=False)

        with pytest.raises(Exception):  # raise_validation_error
            self.client.delete_statement(12345)

    def test_write_entity_revision(self):
        """Test write_entity_revision method."""
        mock_revision_data = MagicMock()

        with patch.object(self.client, 'write_revision') as mock_write:
            mock_write.return_value = MagicMock(success=True)

            result = self.client.write_entity_revision("Q42", 123, mock_revision_data)

            mock_write.assert_called_once_with("Q42", 123, mock_revision_data)

    def test_read_full_revision(self):
        """Test read_full_revision method."""
        mock_result = MagicMock()

        with patch.object(self.client, 'read_revision') as mock_read:
            mock_read.return_value = mock_result

            result = self.client.read_full_revision("Q42", 123)

            assert result == mock_result
            mock_read.assert_called_once_with("Q42", 123)

    def test_load_form_representations_batch(self):
        """Test load_form_representations_batch method."""
        self.client.lexeme_storage = MagicMock()
        self.client.lexeme_storage.load_form_representations_batch.return_value = ["form1", "form2"]

        result = self.client.load_form_representations_batch([1, 2])

        assert result == ["form1", "form2"]
        self.client.lexeme_storage.load_form_representations_batch.assert_called_once_with([1, 2])

    def test_load_sense_glosses_batch(self):
        """Test load_sense_glosses_batch method."""
        self.client.lexeme_storage = MagicMock()
        self.client.lexeme_storage.load_sense_glosses_batch.return_value = ["gloss1", "gloss2"]

        result = self.client.load_sense_glosses_batch([1, 2])

        assert result == ["gloss1", "gloss2"]
        self.client.lexeme_storage.load_sense_glosses_batch.assert_called_once_with([1, 2])

    def test_store_form_representation(self):
        """Test store_form_representation method."""
        self.client.lexeme_storage = MagicMock()
        self.client.lexeme_storage.store_form_representation.return_value = MagicMock(success=True)

        self.client.store_form_representation("text", 12345)

        self.client.lexeme_storage.store_form_representation.assert_called_once_with("text", 12345)

    def test_store_form_representation_failure(self):
        """Test store_form_representation when storage fails."""
        self.client.lexeme_storage = MagicMock()
        self.client.lexeme_storage.store_form_representation.return_value = MagicMock(success=False)

        with pytest.raises(Exception):  # raise_validation_error
            self.client.store_form_representation("text", 12345)

    def test_store_sense_gloss(self):
        """Test store_sense_gloss method."""
        self.client.lexeme_storage = MagicMock()
        self.client.lexeme_storage.store_sense_gloss.return_value = MagicMock(success=True)

        self.client.store_sense_gloss("gloss", 12345)

        self.client.lexeme_storage.store_sense_gloss.assert_called_once_with("gloss", 12345)

    def test_store_sense_gloss_failure(self):
        """Test store_sense_gloss when storage fails."""
        self.client.lexeme_storage = MagicMock()
        self.client.lexeme_storage.store_sense_gloss.return_value = MagicMock(success=False)

        with pytest.raises(Exception):  # raise_validation_error
            self.client.store_sense_gloss("gloss", 12345)
