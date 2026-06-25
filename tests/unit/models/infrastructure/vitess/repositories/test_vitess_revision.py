"""Unit tests for RevisionRepository."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.s3.enums import EditType, EditData, EntityType
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
from models.data.infrastructure.s3.hashes.statements_hashes import StatementsHashes
from models.data.infrastructure.s3.property_counts import PropertyCounts
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.infrastructure.vitess.repositories.revision import RevisionRepository


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

    def test_insert_entity_not_found(self, sample_revision_data):
        """Test insert when entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        from fastapi import HTTPException

        with pytest.raises(HTTPException, match="Entity.*not found"):
            repo.insert_revision("Q999", 1, sample_revision_data, 1234567890123456789)

    def test_get_content_hash_found(self):
        """Test getting content_hash for existing revision."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = (12345678901234567890,)
        mock_vitess_client.cursor = mock_cursor

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        content_hash = repo.get_content_hash(123, 1)

        assert content_hash == 12345678901234567890
        mock_cursor.execute.assert_called_once()

    def test_format_datetime_for_mysql_valid(self):
        """Test formatting valid ISO datetime for MySQL."""
        result = RevisionRepository._format_datetime_for_mysql("2026-01-15T10:30:00Z")
        assert result == "2026-01-15 10:30:00"

    def test_format_datetime_for_mysql_invalid(self):
        """Test formatting invalid ISO datetime returns as-is."""
        result = RevisionRepository._format_datetime_for_mysql("not-a-datetime")
        assert result == "not-a-datetime"

    def test_get_revision_found(self):
        """Test getting revision that exists."""
        import json

        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = (
            json.dumps(["stmt1"]),
            json.dumps(["prop1"]),
            json.dumps({"P31": 1}),
            json.dumps({"en": "123"}),
            json.dumps({"en": "456"}),
            json.dumps({"en": "789"}),
            json.dumps({"enwiki": "101"}),
        )
        mock_vitess_client.cursor = mock_cursor

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.get_revision(123, 1)

        assert result is not None
        assert result.statements == ["stmt1"]
        assert result.properties == ["prop1"]
        assert result.property_counts == {"P31": 1}
        assert result.labels_hashes == {"en": "123"}

    def test_get_revision_not_found(self):
        """Test getting revision that doesn't exist."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.get_revision(999, 1)

        assert result is None

    def test_get_revision_with_none_fields(self):
        """Test getting revision with NULL fields."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = (None, None, None, None, None, None, None)
        mock_vitess_client.cursor = mock_cursor

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.get_revision(123, 1)

        assert result is not None
        assert result.statements == []
        assert result.properties == []
        assert result.property_counts == {}

    def test_get_history_with_results(self):
        """Test getting revision history with results."""
        from datetime import datetime

        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchall.return_value = [
            (1, datetime(2026, 1, 15, 10, 30, 0), 456, "First edit"),
            (2, datetime(2026, 1, 16, 11, 0, 0), 789, "Second edit"),
        ]
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.get_history("Q123", limit=10, offset=0)

        assert len(result) == 2
        assert result[0].revision_id == 1
        assert result[0].user_id == 456
        assert result[0].edit_summary == "First edit"
        assert result[1].revision_id == 2

    def test_get_history_no_results(self):
        """Test getting revision history with no results."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchall.return_value = []
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.get_history("Q123")

        assert result == []

    def test_get_history_entity_not_found(self):
        """Test getting history when entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 0
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.get_history("Q999")

        assert result == []

    def test_delete_connection_not_provided(self):
        """Test delete when database connection not provided."""
        mock_vitess_client = MagicMock()
        mock_connection_manager = MagicMock()
        mock_connection_manager.connection = None
        mock_vitess_client.connection_manager = mock_connection_manager

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.delete("Q123", 1)

        assert result.success is False
        assert "Database connection not provided" in result.error

    def test_delete_entity_not_found(self):
        """Test delete when entity not found."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 0
        mock_connection_manager = MagicMock()
        mock_connection_manager.connection = MagicMock()
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver
        mock_vitess_client.connection_manager = mock_connection_manager

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.delete("Q999", 1)

        assert result.success is False
        assert "Entity not found" in result.error

    def test_delete_success(self):
        """Test successful revision deletion."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_connection_manager = MagicMock()
        mock_connection_manager.connection = MagicMock()
        mock_cursor.fetchone.return_value = (5,)  # current head
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver
        mock_vitess_client.connection_manager = mock_connection_manager

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.delete("Q123", 5)

        assert result.success is True

    def test_get_content_hash_not_found(self):
        """Test getting content_hash for non-existent revision."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        content_hash = repo.get_content_hash(999, 1)

        assert content_hash == 0

    def test_get_content_hash_none_value(self):
        """Test getting content_hash when value is NULL."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = (None,)
        mock_vitess_client.cursor = mock_cursor

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        content_hash = repo.get_content_hash(123, 1)

        assert content_hash == 0

    def test_create_with_cas_entity_not_found(self):
        """Test create_with_cas when entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 0
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

        result = repo.create_with_cas("Q999", 1, entity_data, 12345, 0)

        assert result is False

    def test_create_with_cas_failure(self):
        """Test create_with_cas when CAS fails."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.rowcount = 0
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

        result = repo.create_with_cas(
            "Q123", 2, entity_data, 12345, expected_revision_id=1
        )

        assert result is False

    def test_create_idempotent(self, sample_revision_data):
        """Test creating a revision that already exists is idempotent."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.return_value = (1,)  # COUNT > 0 indicates revision exists
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.create("Q123", 1, sample_revision_data, 12345)

        assert result is True
        # Only called once for the COUNT check, not for INSERT
        assert mock_cursor.execute.call_count == 1

    def test_create_success(self, sample_revision_data):
        """Test creating a revision that doesn't exist yet."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.return_value = (0,)  # COUNT = 0 means revision doesn't exist
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.create("Q123", 1, sample_revision_data, 12345)

        assert result is True
        assert mock_cursor.execute.call_count == 3  # COUNT + INSERT + UPSERT

    def test_insert_revision_with_cas(self, sample_revision_data):
        """Test insert_revision delegating to create_with_cas when expected_revision_id > 0."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.rowcount = 1
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RevisionRepository(vitess_client=mock_vitess_client)

        result = repo.insert_revision("Q123", 1, sample_revision_data, 12345, expected_revision_id=5)

        assert result is True


