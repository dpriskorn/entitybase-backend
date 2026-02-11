"""Integration tests for MetadataRepository using real database."""

import pytest
from models.infrastructure.vitess.repositories.metadata import MetadataRepository


@pytest.fixture
def repository(vitess_client):
    """Create MetadataRepository with real VitessClient."""
    return MetadataRepository(vitess_client=vitess_client)


def test_insert_metadata_content_new(repository, vitess_client):
    """Test inserting new metadata content."""
    repository.insert_metadata_content(12345, "labels")

    cursor = vitess_client.cursor
    cursor.execute(
        "SELECT ref_count FROM metadata_content WHERE content_hash = %s AND content_type = %s",
        (12345, "labels"),
    )
    result = cursor.fetchone()
    assert result[0] == 1


def test_get_metadata_content_exists(repository, vitess_client):
    """Test getting existing metadata content."""
    # Insert first
    repository.insert_metadata_content(12345, "labels")

    # Get metadata
    result = repository.get_metadata_content(12345, "labels")

    assert result.success is True
    assert result.data.ref_count >= 1


def test_get_metadata_content_not_exists(repository):
    """Test getting non-existent metadata content."""
    result = repository.get_metadata_content(99999, "labels")

    assert result.success is False


def test_decrement_ref_count_above_zero(repository, vitess_client):
    """Test decrementing ref_count when it remains above 0."""
    # Insert twice to get ref_count=2
    repository.insert_metadata_content(12345, "labels")
    repository.insert_metadata_content(12345, "labels")

    # Decrement once
    repository.decrement_ref_count(12345, "labels")

    # Verify ref_count=1
    cursor = vitess_client.cursor
    cursor.execute(
        "SELECT ref_count FROM metadata_content WHERE content_hash = %s AND content_type = %s",
        (12345, "labels"),
    )
    result = cursor.fetchone()
    assert result[0] == 1


def test_decrement_ref_count_reaches_zero(repository, vitess_client):
    """Test decrementing ref_count when it reaches 0."""
    # Insert once to get ref_count=1
    repository.insert_metadata_content(12345, "labels")

    # Decrement once
    result = repository.decrement_ref_count(12345, "labels")

    assert result.success is True
    assert result.data is True  # ref_count <= 0


def test_delete_metadata_content(repository, vitess_client):
    """Test deleting metadata content."""
    # Insert and decrement to zero
    repository.insert_metadata_content(12345, "labels")
    repository.decrement_ref_count(12345, "labels")

    # Delete
    repository.delete_metadata_content(12345, "labels")

    # Verify deletion
    cursor = vitess_client.cursor
    cursor.execute(
        "SELECT ref_count FROM metadata_content WHERE content_hash = %s AND content_type = %s",
        (12345, "labels"),
    )
    result = cursor.fetchone()
    assert result is None
