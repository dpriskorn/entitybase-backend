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

    def test_create_with_cas_with_content_hash(self):
        """Test create_with_cas() includes content_hash in INSERT."""
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
            "Q123",
            1,
            entity_data,
            expected_revision_id=0,
            content_hash=12345678901234567890,
        )

        assert result is True
        mock_cursor.execute.assert_called()
        call_args_list = mock_cursor.execute.call_args_list
        for call in call_args_list:
            if call[0][0] and "INSERT INTO entity_revisions" in call[0][0]:
                assert "content_hash" in call[0][0]
