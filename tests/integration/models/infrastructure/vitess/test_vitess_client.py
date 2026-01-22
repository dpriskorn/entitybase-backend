import sys
from typing import Generator

import pytest

sys.path.insert(0, "src")

from models.infrastructure.vitess.client import VitessClient
from models.data.config.vitess import VitessConfig


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

