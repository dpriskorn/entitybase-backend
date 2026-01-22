"""Unit tests for RevisionRepository."""

import pytest
from unittest.mock import MagicMock, patch

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
            "sitelinks_hashes": {},
            "user_id": 456,
            "edit_summary": "Test edit",
        }

        repo.insert("Q123", 1, data)

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
            repo.insert("Q999", 1, {})

    def test_get_revision_found(self):
        """Test getting existing revision."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ('[]', '[]', '{}', '{}', '{}', '{}', '{}')
        mock_vitess_client.cursor = mock_cursor

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.get_revision(123, 1, mock_vitess_client)

        assert result is not None
        assert "statements" in result
        assert result["statements"] == []

    def test_get_revision_not_found(self):
        """Test getting non-existent revision."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.get_revision(123, 1, mock_vitess_client)

        assert result is None

    def test_revert_entity_revision_not_found(self):
        """Test revert when target revision not found."""
        mock_vitess_client = MagicMock()

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        # Mock get_revision to return None
        with patch.object(repo, 'get_revision', return_value=None):
            with pytest.raises(Exception):  # raise_validation_error
                repo.revert_entity(123, 1, 456, "test", None, mock_vitess_client)

    def test_insert_invalid_entity_id(self):
        """Test insert with invalid entity ID."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None  # entity not found
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        with pytest.raises(Exception):  # raise_validation_error
            repo.insert("Q999", 1, {})

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
        assert result["statements"] == ["statement1"]
        assert result["properties"] == {"prop1": "value1"}

    def test_get_revision_null_data(self):
        """Test getting revision with null JSON data."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (None, None, None, None, None, None, None)  # all null
        mock_vitess_client.cursor = mock_cursor

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.get_revision(123, 1, mock_vitess_client)

        assert result is not None
        assert result["statements"] == []
        assert result["properties"] == {}
        assert result["property_counts"] == {}
        assert result["labels_hashes"] == {}
        assert result["descriptions_hashes"] == {}
        assert result["aliases_hashes"] == {}
        assert result["sitelinks_hashes"] == {}
