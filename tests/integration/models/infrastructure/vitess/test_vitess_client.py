import sys
from typing import Generator

import pytest

sys.path.insert(0, "src")

from models.infrastructure.vitess.client import VitessClient
from models.infrastructure.vitess.config import VitessConfig


@pytest.fixture
def vitess_client() -> Generator[VitessClient, None, None]:
    """Create a real VitessClient connected to test database"""
    config = VitessConfig(
        host="vitess",
        port=15309,
        database="page",
        user="root",
        password="",
    )
    client = VitessClient(config)
    yield client


def test_insert_revision_idempotent(vitess_client: VitessClient) -> None:
    """Test that insert_revision is idempotent - calling twice with same params doesn't error"""
    entity_id = "Q123456789"
    revision_id = 1

    vitess_client.register_entity(entity_id)

    vitess_client.insert_revision(
        entity_id=entity_id,
        revision_id=revision_id,
        is_mass_edit=False,
        edit_type="test-edit",
    )

    vitess_client.insert_revision(
        entity_id=entity_id,
        revision_id=revision_id,
        is_mass_edit=False,
        edit_type="test-edit",
    )

    internal_id = vitess_client._resolve_id(entity_id)
    with vitess_client.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM entity_revisions WHERE internal_id = %s AND revision_id = %s",
            (internal_id, revision_id),
        )
        count = cursor.fetchone()[0]
        cursor.close()

        assert count == 1, (
            "Should only have one record, duplicate inserts should be skipped"
        )


def test_insert_revision_different_params(vitess_client: VitessClient) -> None:
    """Test that insert_revision creates separate records for different revisions"""
    entity_id = "Q987654321"

    vitess_client.register_entity(entity_id)

    vitess_client.insert_revision(
        entity_id=entity_id,
        revision_id=1,
        is_mass_edit=False,
        edit_type="first-edit",
    )

    vitess_client.insert_revision(
        entity_id=entity_id,
        revision_id=2,
        is_mass_edit=True,
        edit_type="second-edit",
    )

    internal_id = vitess_client._resolve_id(entity_id)
    with vitess_client.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM entity_revisions WHERE internal_id = %s",
            (internal_id,),
        )
        count = cursor.fetchone()[0]
        cursor.close()

        assert count == 2, "Should have two separate records for different revisions"


def test_create_revision_cas_success(vitess_client: VitessClient) -> None:
    """Test create_revision with CAS succeeds when expected_revision_id matches"""
    entity_id = "Q111111111"
    revision_id = 1

    vitess_client.register_entity(entity_id)

    # Create revision without CAS first
    data = {
        "schema_version": 1,
        "revision_id": revision_id,
        "created_at": "2023-01-01T00:00:00Z",
        "created_by": "test",
        "entity_type": "item",
        "entity": {"id": entity_id, "type": "item"},
        "statements": [],
        "properties": [],
        "property_counts": {},
        "content_hash": 0,
        "edit_summary": "test",
        "is_mass_edit": False,
        "edit_type": "test",
        "is_semi_protected": False,
        "is_locked": False,
        "is_archived": False,
        "is_dangling": False,
        "is_mass_edit_protected": False,
        "is_deleted": False,
        "is_redirect": False,
    }

    vitess_client.create_revision(entity_id, revision_id, data)

    # Now create another revision with CAS, expected head should be 1
    revision_id2 = 2
    data2 = data.copy()
    data2["revision_id"] = revision_id2

    # Should succeed since expected=1 matches current head
    vitess_client.create_revision(
        entity_id, revision_id2, data2, expected_revision_id=1
    )

    # Verify head is now 2
    head = vitess_client.get_head(entity_id)
    assert head == 2


def test_create_revision_cas_failure(vitess_client: VitessClient) -> None:
    """Test create_revision with CAS fails when expected_revision_id doesn't match"""

    entity_id = "Q222222222"
    revision_id = 1

    vitess_client.register_entity(entity_id)

    data = {
        "schema_version": 1,
        "revision_id": revision_id,
        "created_at": "2023-01-01T00:00:00Z",
        "created_by": "test",
        "entity_type": "item",
        "entity": {"id": entity_id, "type": "item"},
        "statements": [],
        "properties": [],
        "property_counts": {},
        "content_hash": 0,
        "edit_summary": "test",
        "is_mass_edit": False,
        "edit_type": "test",
        "is_semi_protected": False,
        "is_locked": False,
        "is_archived": False,
        "is_dangling": False,
        "is_mass_edit_protected": False,
        "is_deleted": False,
        "is_redirect": False,
    }

    vitess_client.create_revision(entity_id, revision_id, data)

    # Try to create another with wrong expected (e.g., 2 instead of 1)
    revision_id2 = 2
    data2 = data.copy()
    data2["revision_id"] = revision_id2

    with pytest.raises(ValueError) as exc_info:
        vitess_client.create_revision(
            entity_id, revision_id2, data2, expected_revision_id=2
        )

    assert "Concurrent modification detected" in str(exc_info.value)


def test_set_redirect_target_cas_success(vitess_client: VitessClient) -> None:
    """Test set_redirect_target with CAS succeeds when expected matches"""
    entity_id = "Q333333333"
    redirect_to = "Q444444444"

    vitess_client.register_entity(entity_id)
    vitess_client.register_entity(redirect_to)

    # Set redirect without CAS first
    vitess_client.set_redirect_target(entity_id, redirect_to)

    # Now set again with CAS, expected should be the internal_id of redirect_to
    # But since it's string, wait, expected is int? Wait, in the code, expected_redirects_to is int | None, which is internal_id.

    # For CAS, expected is the current redirects_to internal_id.

    # Since we set to redirect_to, expected should be its internal_id.

    internal_redirect_to = vitess_client._resolve_id(redirect_to)
    assert internal_redirect_to is not None

    # This should succeed
    vitess_client.set_redirect_target(
        entity_id, redirect_to, expected_redirects_to=internal_redirect_to
    )

    # Verify it's still set
    target = vitess_client.get_redirect_target(entity_id)
    assert target == redirect_to


def test_set_redirect_target_cas_failure(vitess_client: VitessClient) -> None:
    """Test set_redirect_target with CAS fails when expected doesn't match"""

    entity_id = "Q555555555"
    redirect_to1 = "Q666666666"
    redirect_to2 = "Q777777777"

    vitess_client.register_entity(entity_id)
    vitess_client.register_entity(redirect_to1)
    vitess_client.register_entity(redirect_to2)

    # Set to redirect_to1
    vitess_client.set_redirect_target(entity_id, redirect_to1)

    # Try to set to redirect_to2 with wrong expected (e.g., None or wrong id)
    with pytest.raises(ValueError) as exc_info:
        self.state.vitess_client.set_redirect_target(
            entity_id, redirect_to2, expected_redirects_to=999
        )  # Wrong expected

    assert "Concurrent redirect modification detected" in str(exc_info.value)
