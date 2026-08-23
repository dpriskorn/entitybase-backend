"""Integration tests for HeadRepository using real database."""

import pytest

from models.infrastructure.db.repositories.head import HeadRepository
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.data.infrastructure.s3.enums import EntityType, EditType, EditData
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps


@pytest.fixture
def repository(db_client):
    """Create HeadRepository instance with real Vitess client."""
    return HeadRepository(db_client=db_client)


def test_get_head_revision_exists(repository, db_client):
    """Test getting head revision when entity exists."""
    entity_id = "Q333333333"
    revision_id = 30

    # Register entity and insert revision
    db_client.register_entity(entity_id)
    db_client.entity_repository.create_entity(entity_id)
    revision_data = RevisionData(
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
    )
    db_client.insert_revision(
        entity_id=entity_id,
        revision_id=revision_id,
        entity_data=revision_data,
        content_hash=333333333,
    )

    # Get internal ID
    internal_id = db_client.resolve_id(entity_id)

    # Get head revision
    result = repository.get_head_revision(internal_id)

    assert result.success is True
    assert result.data == revision_id


def test_get_head_revision_not_exists(repository):
    """Test getting head revision when entity doesn't exist."""
    result = repository.get_head_revision(999999)

    assert result.success is False
    assert "not found" in result.error


def test_get_head_revision_invalid_id(repository):
    """Test getting head revision with invalid internal ID."""
    result = repository.get_head_revision(0)

    assert result.success is False
    assert "Invalid" in result.error
