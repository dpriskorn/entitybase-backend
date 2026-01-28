"""Integration tests for HeadRepository using real database."""

import pytest

from models.infrastructure.vitess.repositories.head import HeadRepository
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.data.infrastructure.s3.enums import EntityType, EditType, EditData
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps


@pytest.fixture
def repository(vitess_client):
    """Create HeadRepository instance with real Vitess client."""
    return HeadRepository(vitess_client=vitess_client)


def test_cas_update_with_status_success(repository, vitess_client):
    """Test successful CAS update with status flags."""
    entity_id = "Q123456789"
    
    # Register entity and set initial head
    vitess_client.register_entity(entity_id)
    vitess_client.entity_repository.create_entity(entity_id)
    revision_data = RevisionData(
        revision_id=0,
        entity_type=EntityType.ITEM,
        edit=EditData(type=EditType.MANUAL_UPDATE, user_id=0, mass=False, summary="Initial", at="2025-01-01T00:00:00Z"),
        hashes=HashMaps(),
    )
    vitess_client.insert_revision(entity_id=entity_id, revision_id=0, entity_data=revision_data)
    
    # Perform CAS update
    result = repository.cas_update_with_status(
        entity_id=entity_id,
        expected_head=0,
        new_head=10,
        is_semi_protected=True,
        is_locked=False,
        is_archived=False,
        is_dangling=False,
        is_mass_edit_protected=True,
        is_deleted=False,
        is_redirect=False,
    )
    
    assert result.success is True
    assert result.error is ""


def test_cas_update_with_status_failure(repository, vitess_client):
    """Test CAS update when head doesn't match expected value."""
    entity_id = "Q987654321"
    
    # Register entity and set head to 10
    vitess_client.register_entity(entity_id)
    vitess_client.entity_repository.create_entity(entity_id)
    revision_data = RevisionData(
        revision_id=10,
        entity_type=EntityType.ITEM,
        edit=EditData(type=EditType.MANUAL_UPDATE, user_id=0, mass=False, summary="Test", at="2025-01-01T00:00:00Z"),
        hashes=HashMaps()
    )
    vitess_client.insert_revision(entity_id=entity_id, revision_id=10, entity_data=revision_data)
    
    # Try to CAS update with wrong expected head
    result = repository.cas_update_with_status(
        entity_id=entity_id,
        expected_head=5,
        new_head=15,
    )
    
    assert result.success is False
    assert "CAS failed" in result.error


def test_cas_update_with_status_entity_not_found(repository):
    """Test CAS update when entity doesn't exist."""
    result = repository.cas_update_with_status("Q999", 0, 10)
    
    assert result.success is False
    assert "not found" in result.error.lower()


def test_hard_delete(repository, vitess_client):
    """Test hard delete operation."""
    entity_id = "Q111111111"
    head_revision_id = 20
    
    # Register entity and set head
    vitess_client.register_entity(entity_id)
    vitess_client.entity_repository.create_entity(entity_id)
    revision_data = RevisionData(
        revision_id=head_revision_id,
        entity_type=EntityType.ITEM,
        edit=EditData(type=EditType.MANUAL_UPDATE, user_id=0, mass=False, summary="Test", at="2025-01-01T00:00:00Z"),
        hashes=HashMaps(),
    )
    vitess_client.insert_revision(entity_id=entity_id, revision_id=head_revision_id, entity_data=revision_data)
    
    # Perform hard delete
    result = repository.hard_delete(entity_id, head_revision_id)
    
    assert result.success is True


def test_hard_delete_entity_not_found(repository):
    """Test hard delete when entity doesn't exist."""
    result = repository.hard_delete("Q999", 15)
    
    assert result.success is False
    assert "not found" in result.error.lower()


def test_soft_delete(repository, vitess_client):
    """Test soft delete operation."""
    entity_id = "Q222222222"
    
    # Register entity and set head
    vitess_client.register_entity(entity_id)
    vitess_client.entity_repository.create_entity(entity_id)
    revision_data = RevisionData(
        revision_id=10,
        entity_type=EntityType.ITEM,
        edit=EditData(type=EditType.MANUAL_UPDATE, user_id=0, mass=False, summary="Test", at="2025-01-01T00:00:00Z"),
        hashes=HashMaps(),
    )
    vitess_client.insert_revision(entity_id=entity_id, revision_id=10, entity_data=revision_data)
    
    # Perform soft delete
    result = repository.soft_delete(entity_id)
    
    assert result.success is True


def test_soft_delete_entity_not_found(repository):
    """Test soft delete when entity doesn't exist."""
    result = repository.soft_delete("Q999")
    
    assert result.success is False
    assert "not found" in result.error.lower()


def test_get_head_revision_exists(repository, vitess_client):
    """Test getting head revision when entity exists."""
    entity_id = "Q333333333"
    revision_id = 30
    
    # Register entity and insert revision
    vitess_client.register_entity(entity_id)
    vitess_client.entity_repository.create_entity(entity_id)
    revision_data = RevisionData(
        revision_id=revision_id,
        entity_type=EntityType.ITEM,
        edit=EditData(type=EditType.MANUAL_UPDATE, user_id=0, mass=False, summary="Test", at="2025-01-01T00:00:00Z"),
        hashes=HashMaps(),
    )
    vitess_client.insert_revision(entity_id=entity_id, revision_id=revision_id, entity_data=revision_data)
    
    # Get internal ID
    internal_id = vitess_client.resolve_id(entity_id)
    
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