import pytest

from models.infrastructure.vitess.id_resolver import IdResolver


@pytest.mark.integration
def test_id_resolver_resolve_id(db_conn):
    """Test IdResolver.resolve_id with real database."""
    resolver = IdResolver(None)  # connection_manager not needed for static method

    # Insert a test entity_id_mapping
    test_entity_id = "Q999999"
    test_internal_id = 999999
    with db_conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO entity_id_mapping (entity_id, internal_id) VALUES (%s, %s)",
            (test_entity_id, test_internal_id),
        )
    db_conn.commit()

    # Test resolve_id
    resolved_id = IdResolver.resolve_id(db_conn, test_entity_id)
    assert resolved_id == test_internal_id

    # Test non-existent
    non_existent_id = IdResolver.resolve_id(db_conn, "Q000000")
    assert non_existent_id == 0

    # Clean up
    with db_conn.cursor() as cursor:
        cursor.execute(
            "DELETE FROM entity_id_mapping WHERE entity_id = %s", (test_entity_id,)
        )
    db_conn.commit()
