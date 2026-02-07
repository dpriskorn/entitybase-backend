import pytest
import time as time_module


@pytest.fixture(autouse=True)
def test_timer():
    """Auto-apply timing to all tests."""
    start = time_module.time()
    print(f"\n=== TEST START: {start} ===")
    yield
    print(
        f"=== TEST END: {time_module.time()}, duration: {(time_module.time() - start):.2f}s ==="
    )


@pytest.mark.integration
def test_id_resolver_resolve_id(db_conn, vitess_client):
    """Test IdResolver.resolve_id with real database."""
    import time as time_module

    print(f"=== test_id_resolver_resolve_id START: {time_module.time()} ===")

    # Create a VitessClient to get proper IdResolver
    resolver = vitess_client.id_resolver

    # Insert a test entity_id_mapping
    insert_start = time_module.time()
    test_entity_id = "Q999999"
    test_internal_id = 999999
    with db_conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO entity_id_mapping (entity_id, internal_id) VALUES (%s, %s)",
            (test_entity_id, test_internal_id),
        )
    db_conn.commit()
    print(f"Insert took {(time_module.time() - insert_start):.4f}s")

    # Test resolve_id
    resolve_start = time_module.time()
    resolved_id = resolver.resolve_id(test_entity_id)
    print(f"Resolve ID took {(time_module.time() - resolve_start):.4f}s")
    assert resolved_id == test_internal_id

    # Test non-existent
    resolve_none_start = time_module.time()
    non_existent_id = resolver.resolve_id("Q000000")
    print(
        f"Resolve non-existent ID took {(time_module.time() - resolve_none_start):.4f}s"
    )
    assert non_existent_id == 0

    # Clean up
    delete_start = time_module.time()
    with db_conn.cursor() as cursor:
        cursor.execute(
            "DELETE FROM entity_id_mapping WHERE entity_id = %s", (test_entity_id,)
        )
    db_conn.commit()
    print(f"Delete took {(time_module.time() - delete_start):.4f}s")

    print(
        f"=== test_id_resolver_resolve_id END: {time_module.time()}, total: {(time_module.time() - insert_start):.2f}s ==="
    )
