import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

pytestmark = pytest.mark.unit

from models.infrastructure.vitess.revision_repository import RevisionRepository


class TestRevisionRepository:
    def test_init(self):
        """Test RevisionRepository initialization."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()

        repo = RevisionRepository(mock_connection_manager, mock_id_resolver)

        assert repo.connection_manager == mock_connection_manager
        assert repo.id_resolver == mock_id_resolver

    def test_insert_success(self):
        """Test successful revision insertion."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = RevisionRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 123
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        data = {
            "is_mass_edit": True,
            "edit_type": "test",
            "statements": [{"id": "P1"}],
            "properties": [{"type": "string"}],
            "property_counts": {"P1": 1},
            "labels_hashes": {"en": "hash1"},
            "descriptions_hashes": {"en": "hash2"},
            "aliases_hashes": {"en": ["hash3"]},
            "sitelinks_hashes": {"enwiki": "hash4"},
            "user_id": 456,
            "edit_summary": "Test edit",
        }

        repo.insert(mock_conn, "Q42", 789, data)

        mock_id_resolver.resolve_id.assert_called_once_with(mock_conn, "Q42")
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args
        assert "INSERT INTO entity_revisions" in call_args[0][0]
        assert call_args[0][1][1] == 789  # revision_id
        assert call_args[0][1][2] is True  # is_mass_edit

    @patch("models.infrastructure.vitess.revision_repository.raise_validation_error")
    def test_insert_entity_not_found(self, mock_raise):
        """Test insert when entity not found."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()

        repo = RevisionRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 0  # Not found

        repo.insert(mock_conn, "Q999", 123, {})

        mock_raise.assert_called_once_with("Entity Q999 not found", status_code=404)

    def test_get_revision_success(self):
        """Test successful revision retrieval."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_vitess = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = RevisionRepository(mock_connection_manager, mock_id_resolver)
        mock_vitess.get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock database row
        mock_cursor.fetchone.return_value = (
            '[{"id": "P1"}]',  # statements
            '[{"type": "string"}]',  # properties
            '{"P1": 1}',  # property_counts
            '{"en": "hash1"}',  # labels_hashes
            '{"en": "hash2"}',  # descriptions_hashes
            '{"en": ["hash3"]}',  # aliases_hashes
            '{"enwiki": "hash4"}',  # sitelinks_hashes
        )

        result = repo.get_revision(123, 456, mock_vitess)

        assert result["statements"] == [{"id": "P1"}]
        assert result["properties"] == [{"type": "string"}]
        assert result["property_counts"] == {"P1": 1}
        assert result["labels_hashes"] == {"en": "hash1"}
        assert result["descriptions_hashes"] == {"en": "hash2"}
        assert result["aliases_hashes"] == {"en": ["hash3"]}
        assert result["sitelinks_hashes"] == {"enwiki": "hash4"}

    def test_get_revision_not_found(self):
        """Test get_revision when revision not found."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_vitess = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = RevisionRepository(mock_connection_manager, mock_id_resolver)
        mock_vitess.get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = repo.get_revision(123, 456, mock_vitess)

        assert result is None

    def test_revert_entity_revision_not_found(self):
        """Test revert_entity when target revision not found."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_vitess = MagicMock()

        repo = RevisionRepository(mock_connection_manager, mock_id_resolver)
        # Mock get_revision to return None
        with patch.object(repo, "get_revision", return_value=None):
            with pytest.raises(ValueError) as exc_info:
                repo.revert_entity(123, 456, 789, "Test reason", None, mock_vitess)

        assert "Revision 456 not found" in str(exc_info.value)

    def test_revert_entity_success(self):
        """Test successful entity revert."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_vitess = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = RevisionRepository(mock_connection_manager, mock_id_resolver)

        # Mock get_revision to return target data
        target_data = {
            "statements": [{"id": "P1"}],
            "properties": [{"type": "string"}],
            "property_counts": {"P1": 1},
            "labels_hashes": {"en": "hash1"},
            "descriptions_hashes": {"en": "hash2"},
            "aliases_hashes": {"en": ["hash3"]},
        }

        with patch.object(repo, "get_revision", return_value=target_data):
            mock_vitess.get_connection.return_value.__enter__.return_value = mock_conn
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_cursor.fetchone.return_value = [100]  # new_revision_id
            mock_vitess.id_resolver.resolve_entity_id.return_value = "Q42"
            mock_vitess.user_repository.log_user_activity = MagicMock()

            result = repo.revert_entity(
                123, 456, 789, "Test reason", {"test": "data"}, mock_vitess
            )

        assert result == 100
        assert (
            mock_cursor.execute.call_count >= 3
        )  # get next ID, insert revision, update head

    def test_get_history_success(self):
        """Test successful history retrieval."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = RevisionRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 123
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock database rows
        mock_datetime = MagicMock()
        mock_datetime.isoformat.return_value = "2023-01-01T12:00:00"
        mock_cursor.fetchall.return_value = [
            (456, mock_datetime, 789, "Test edit"),
            (455, None, 788, "Previous edit"),
        ]

        result = repo.get_history(mock_conn, "Q42", limit=10, offset=5)

        assert len(result) == 2
        assert result[0].revision_id == 456
        assert result[0].created_at == "2023-01-01T12:00:00"
        assert result[0].user_id == 789
        assert result[0].edit_summary == "Test edit"
        assert result[1].revision_id == 455
        assert result[1].created_at == ""

    def test_get_history_entity_not_found(self):
        """Test get_history when entity not found."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()

        repo = RevisionRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 0  # Not found

        result = repo.get_history(mock_conn, "Q999")

        assert result == []

    def test_delete_success(self):
        """Test successful revision deletion."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = RevisionRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 123
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        repo.delete(mock_conn, "Q42", 456)

        assert mock_cursor.execute.call_count == 2  # DELETE and UPDATE

    def test_delete_entity_not_found(self):
        """Test delete when entity not found."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()

        repo = RevisionRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 0  # Not found

        repo.delete(mock_conn, "Q999", 456)

        # Should not execute any SQL
        mock_conn.cursor.assert_not_called()

    def test_create_with_cas_success(self):
        """Test successful create with compare-and-swap."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = RevisionRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 123
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1  # Affected rows

        data = {
            "is_mass_edit": True,
            "edit_type": "test",
            "hashes": [{"id": "P1"}],
            "properties": [{"type": "string"}],
            "property_counts": {"P1": 1},
            "is_semi_protected": False,
            "is_locked": False,
            "is_archived": False,
            "is_dangling": False,
            "is_mass_edit_protected": False,
        }

        result = repo.create_with_cas(mock_conn, "Q42", 789, data, 456)

        assert result is True
        assert mock_cursor.execute.call_count == 2  # INSERT and UPDATE

    def test_create_with_cas_entity_not_found(self):
        """Test create_with_cas when entity not found."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()

        repo = RevisionRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 0  # Not found

        result = repo.create_with_cas(mock_conn, "Q999", 123, {}, 456)

        assert result is False

    def test_create_success(self):
        """Test successful revision creation."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = RevisionRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 123
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        data = {
            "is_mass_edit": True,
            "edit_type": "test",
            "hashes": [{"id": "P1"}],
            "properties": [{"type": "string"}],
            "property_counts": {"P1": 1},
            "is_semi_protected": False,
            "is_locked": False,
            "is_archived": False,
            "is_dangling": False,
            "is_mass_edit_protected": False,
        }

        repo.create(mock_conn, "Q42", 789, data)

        assert mock_cursor.execute.call_count == 2  # INSERT into revisions and head

    @patch("models.infrastructure.vitess.revision_repository.raise_validation_error")
    def test_create_entity_not_found(self, mock_raise):
        """Test create when entity not found."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()

        repo = RevisionRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 0  # Not found

        repo.create(mock_conn, "Q999", 123, {})

        mock_raise.assert_called_once_with("Entity Q999 not found", status_code=404)
