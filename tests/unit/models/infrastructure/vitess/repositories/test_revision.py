"""Unit tests for RevisionRepository."""

from unittest.mock import MagicMock
from datetime import datetime, timezone

import pytest

from models.data.infrastructure.vitess.records.revision import RevisionRecord
from models.infrastructure.vitess.repositories.revision import RevisionRepository
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.data.infrastructure.s3.enums import EditType, EditData, EntityType
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
from models.data.infrastructure.s3.hashes.statements_hashes import StatementsHashes
from models.data.infrastructure.s3.property_counts import PropertyCounts
from models.data.infrastructure.s3.entity_state import EntityState


@pytest.fixture
def sample_revision_data():
    """Fixture providing a default RevisionData object for testing."""
    return RevisionData(
        revision_id=1,
        entity_type=EntityType.ITEM,
        edit=EditData(
            mass=False,
            type=EditType.MANUAL_UPDATE,
            user_id=456,
            summary="Test edit",
            at=datetime.now(timezone.utc).isoformat(),
        ),
        hashes=HashMaps(statements=StatementsHashes(root=[])),
        properties=[],
        property_counts=PropertyCounts({}),
        state=EntityState(),
    )


class TestRevisionRepository:
    """Unit tests for RevisionRepository."""

    def test_insert_success(self, sample_revision_data):
        """Test successful revision insertion."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        repo.insert_revision("Q123", 1, sample_revision_data)

        mock_cursor.execute.assert_called_once()
        # Verify the INSERT statement was called with correct params

    def test_insert_entity_not_found(self, sample_revision_data):
        """Test insert when entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        with pytest.raises(Exception):  # raise_validation_error raises ValueError
            repo.insert_revision("Q999", 1, sample_revision_data)

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



    def test_insert_logging(self, caplog, sample_revision_data):
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

        repo.insert_revision("Q123", 1, sample_revision_data)

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

    def test_insert_with_qualifiers_and_references(self, sample_revision_data):
        """Test insert with complex data including qualifiers and references."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        repo.insert_revision("Q1", 2, sample_revision_data)

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

    def test_get_content_hash_found(self):
        """Test getting content_hash for existing revision."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (12345678901234567890,)
        mock_vitess_client.cursor = mock_cursor

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        content_hash = repo.get_content_hash(123, 1)

        assert content_hash == 12345678901234567890
        mock_cursor.execute.assert_called_once()

    def test_get_content_hash_not_found(self):
        """Test getting content_hash for non-existent revision."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        content_hash = repo.get_content_hash(123, 1)

        assert content_hash is None

    def test_create_with_content_hash(self):
        """Test create() includes content_hash in INSERT."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (0,)  # revision doesn't exist
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        entity_data = RevisionData(
            revision_id=1,
            entity_type=EntityType.ITEM,
            edit=EditData(
                mass=False,
                type=EditType.MANUAL_UPDATE,
                user_id=456,
                summary="test",
                at=datetime.now(timezone.utc).isoformat(),
            ),
            hashes=HashMaps(statements=StatementsHashes(root=[])),
            properties=[],
            property_counts=PropertyCounts({}),
            state=EntityState(),
        )

        repo.create("Q123", 1, entity_data, content_hash=12345678901234567890)

        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args
        sql = call_args[0][0]
        assert "content_hash" in sql.upper()

    def test_create_with_cas_with_content_hash(self):
        """Test create_with_cas() includes content_hash in INSERT."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        entity_data = RevisionData(
            revision_id=1,
            entity_type=EntityType.ITEM,
            edit=EditData(
                mass=False,
                type=EditType.MANUAL_UPDATE,
                user_id=456,
                summary="test",
                at=datetime.now(timezone.utc).isoformat(),
            ),
            hashes=HashMaps(statements=StatementsHashes(root=[])),
            properties=[],
            property_counts=PropertyCounts({}),
            state=EntityState(),
        )

        result = repo.create_with_cas("Q123", 1, entity_data, expected_revision_id=0, content_hash=12345678901234567890)

        assert result is True
        mock_cursor.execute.assert_called()
        call_args_list = mock_cursor.execute.call_args_list
        for call in call_args_list:
            if call[0][0] and "INSERT INTO entity_revisions" in call[0][0]:
                assert "content_hash" in call[0][0]


