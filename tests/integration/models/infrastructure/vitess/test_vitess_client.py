import sys

sys.path.insert(0, "src")

from models.infrastructure.s3.revision.revision_data import RevisionData
from models.data.infrastructure.s3.enums import EntityType, EditType, EditData
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps


def create_minimal_revision_data(revision_id: int) -> RevisionData:
    """Create a minimal valid RevisionData for testing."""
    return RevisionData(
        revision_id=revision_id,
        entity_type=EntityType.ITEM,
        edit=EditData(
            type=EditType.MANUAL_UPDATE,
            user_id=0,
            mass=False,
            summary="Test revision",
            at="2025-01-01T00:00:00Z",
        ),
        hashes=HashMaps(),
    )


def test_insert_revision_idempotent(vitess_client) -> None:
    """Test that insert_revision is idempotent - calling twice with same params doesn't error"""
    entity_id = "Q123456789"
    revision_id = 1

    vitess_client.register_entity(entity_id)

    entity_data = create_minimal_revision_data(revision_id)

    vitess_client.insert_revision(
        entity_id=entity_id,
        revision_id=revision_id,
        entity_data=entity_data,
        content_hash=123456789,
    )

    vitess_client.insert_revision(
        entity_id=entity_id,
        revision_id=revision_id,
        entity_data=entity_data,
        content_hash=123456789,
    )

    internal_id = vitess_client.resolve_id(entity_id)
    cursor = vitess_client.cursor
    cursor.execute(
        "SELECT COUNT(*) FROM entity_revisions WHERE internal_id = %s AND revision_id = %s",
        (internal_id, revision_id),
    )
    count = cursor.fetchone()[0]

    assert count == 1, (
        "Should only have one record, duplicate inserts should be skipped"
    )


def test_insert_revision_different_params(vitess_client) -> None:
    """Test that insert_revision creates separate records for different revisions"""
    entity_id = "Q987654321"

    vitess_client.register_entity(entity_id)

    entity_data_1 = create_minimal_revision_data(1)
    entity_data_2 = create_minimal_revision_data(2)

    vitess_client.insert_revision(
        entity_id=entity_id,
        revision_id=1,
        entity_data=entity_data_1,
        content_hash=111111111,
    )

    vitess_client.insert_revision(
        entity_id=entity_id,
        revision_id=2,
        entity_data=entity_data_2,
        content_hash=222222222,
    )

    internal_id = vitess_client.resolve_id(entity_id)
    cursor = vitess_client.cursor
    cursor.execute(
        "SELECT COUNT(*) FROM entity_revisions WHERE internal_id = %s",
        (internal_id,),
    )
    count = cursor.fetchone()[0]

    assert count == 2, "Should have two separate records for different revisions"
