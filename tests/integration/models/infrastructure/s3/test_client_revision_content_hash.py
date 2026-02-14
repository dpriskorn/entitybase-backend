"""Integration tests for S3 client revision content hash operations."""

import pytest
from fastapi import HTTPException

from models.data.infrastructure.s3.enums import EntityType, EditType, EditData
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.s3.revision_data import S3RevisionData
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.infrastructure.s3.client import MyS3Client


def create_minimal_revision_data(entity_id: str, revision_id: int) -> RevisionData:
    """Create minimal revision data for testing."""
    return RevisionData(
        revision_id=revision_id,
        entity_type=EntityType.ITEM,
        edit=EditData(
            type=EditType.MANUAL_UPDATE,
            user_id=0,
            mass=False,
            summary="Test",
            at="2025-01-01T00:00:00Z",
        ),
        hashes=HashMaps(),
        schema_version="4.0.0",
        created_at="2025-01-01T00:00:00Z",
        redirects_to="",
        state=EntityState(),
        property_counts=None,
        properties=[],
    )


class TestS3ClientRevisionReadWithContentHash:
    """Integration tests for S3Client revision reading with content hash."""

    def test_read_revision_queries_database_first(self, s3_client, vitess_client):
        """Test that read_revision queries database first for content hash."""
        entity_id = "Q123"
        revision_id = 1

        vitess_client.register_entity(entity_id)
        entity_data = create_minimal_revision_data(entity_id, revision_id)
        content_hash = 123456789

        s3_revision_data = S3RevisionData(
            schema="4.0.0",
            revision=entity_data.model_dump(),
            hash=content_hash,
            created_at="2025-01-01T00:00:00Z",
        )
        s3_client.store_revision(
            content_hash=content_hash, revision_data=s3_revision_data
        )
        vitess_client.insert_revision(
            entity_id=entity_id,
            revision_id=revision_id,
            entity_data=entity_data,
            content_hash=content_hash,
        )

        result = s3_client.read_revision(entity_id=entity_id, revision_id=revision_id)

        assert result is not None
        assert result.revision["revision_id"] == revision_id

    def test_read_revision_entity_not_found(self, s3_client, vitess_client):
        """Test that read_revision raises error for non-existent entity."""
        entity_id = "Q999"
        revision_id = 1

        with pytest.raises(HTTPException):
            s3_client.read_revision(entity_id=entity_id, revision_id=revision_id)

    def test_read_revision_revision_not_found(self, s3_client, vitess_client):
        """Test that read_revision raises error for non-existent revision."""
        entity_id = "Q123"
        revision_id = 999

        vitess_client.register_entity(entity_id)
        with pytest.raises(HTTPException):
            s3_client.read_revision(entity_id=entity_id, revision_id=revision_id)

    def test_read_revision_end_to_end(self, s3_client, vitess_client):
        """Test end-to-end read_revision operation."""
        entity_id = "Q456"
        revision_id = 2

        vitess_client.register_entity(entity_id)
        entity_data = create_minimal_revision_data(entity_id, revision_id)
        content_hash = 987654321

        s3_revision_data = S3RevisionData(
            schema="4.0.0",
            revision=entity_data.model_dump(),
            hash=content_hash,
            created_at="2025-01-01T00:00:00Z",
        )
        s3_client.store_revision(
            content_hash=content_hash, revision_data=s3_revision_data
        )
        vitess_client.insert_revision(
            entity_id=entity_id,
            revision_id=revision_id,
            entity_data=entity_data,
            content_hash=content_hash,
        )

        result = s3_client.read_revision(entity_id=entity_id, revision_id=revision_id)

        assert result is not None
        assert result.revision["revision_id"] == revision_id
