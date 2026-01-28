"""Unit tests for RevisionRepository."""

from unittest.mock import MagicMock

import pytest

from models.data.infrastructure.vitess.records.revision import RevisionRecord
from models.infrastructure.vitess.repositories.revision import RevisionRepository


class TestRevisionRepository:
    """Unit tests for RevisionRepository."""

    def test_insert_success(self):
        """Test successful revision insertion."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        data = {
            "is_mass_edit": False,
            "edit_type": "edit",
            "statements": [{"property": "P31"}],
            "properties": ["P31"],
            "property_counts": {"P31": 1},
            "labels_hashes": {},
            "descriptions_hashes": {},
            "aliases_hashes": {},
            "sitelinks": {},
            "user_id": 456,
            "edit_summary": "Test edit",
        }

        repo.insert_revision("Q123", 1, data)

        mock_cursor.execute.assert_called_once()
        # Verify the INSERT statement was called with correct params

    def test_insert_entity_not_found(self):
        """Test insert when entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        with pytest.raises(Exception):  # raise_validation_error raises ValueError
            repo.insert_revision("Q999", 1, {})

    def test_get_revision_found(self):
        """Test getting existing revision."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ('[]', '[]', '{}', '{}', '{}', '{}', '{}')
        mock_vitess_client.cursor = mock_cursor

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.get_revision(123, 1, mock_vitess_client)

        assert result is not None
        assert isinstance(result, RevisionRecord)
        assert result.statements == []

    def test_get_revision_not_found(self):
        """Test getting non-existent revision."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.get_revision(123, 1, mock_vitess_client)

        assert result is None



    def test_insert_invalid_entity_id(self):
        """Test insert with invalid entity ID."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None  # entity not found
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

    def test_insert_logging(self, caplog):
        """Test that insert logs debug message."""
        import logging
        caplog.set_level(logging.DEBUG)
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        data = {"user_id": 456}
        repo.insert_revision("Q123", 1, data)

        assert "Inserting revision 1 for entity Q123" in caplog.text

    def test_get_revision_logging(self, caplog):
        """Test that get_revision logs debug message."""
        import logging
        caplog.set_level(logging.DEBUG)
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ('[]', '[]', '{}', '{}', '{}', '{}', '{}')
        mock_vitess_client.cursor = mock_cursor

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        repo.get_revision(123, 1, mock_vitess_client)

        assert "Getting revision 1 for entity 123" in caplog.text



        with pytest.raises(Exception):  # raise_validation_error
            repo.insert_revision("Q999", 1, {})

    def test_get_revision_with_data(self):
        """Test getting revision with JSON data."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        # Simulate JSON strings in DB
        mock_cursor.fetchone.return_value = ('["statement1"]', '{"prop1": "value1"}', '{"count": 1}', '{"hash1": "term1"}', '{"hash2": "term2"}', '{"hash3": "term3"}', '{"hash4": "term4"}')
        mock_vitess_client.cursor = mock_cursor

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.get_revision(123, 1, mock_vitess_client)

        assert result is not None
        assert isinstance(result, RevisionRecord)
        assert result.statements == ["statement1"]
        assert result.properties == {"prop1": "value1"}

    def test_insert_with_qualifiers_and_references(self):
        """Test insert with complex data including qualifiers and references."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        data = {
            "is_mass_edit": True,
            "edit_type": "mass_edit",
            "statements": [{"prop": "P31", "value": "Q5"}],
            "properties": ["P31"],
            "property_counts": {"P31": 1},
            "labels_hashes": {"en": "hash1"},
            "descriptions_hashes": {"en": "hash2"},
            "aliases_hashes": {"en": "hash3"},
            "sitelinks": {"enwiki": {"title_hash": "hash4", "badges": []}},
            "user_id": 456,
            "edit_summary": "Mass edit summary",
        }

        repo.insert_revision("Q1", 2, data)

        mock_cursor.execute.assert_called_once()
        # Verify the call includes all fields

    def test_get_revision_no_rows(self):
        """Test getting revision when no rows returned."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.get_revision(123, 1, mock_vitess_client)

        assert result is None


