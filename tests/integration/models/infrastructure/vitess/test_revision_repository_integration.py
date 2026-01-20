import pytest

from models.infrastructure.vitess.repositories.revision import RevisionRepository
from models.infrastructure.vitess.vitess_client import VitessClient
from models.infrastructure.vitess.config import VitessConfig


@pytest.mark.integration
def test_revision_repository_insert_and_get(db_conn):
    """Test RevisionRepository insert and get with real database."""
    # Create a mock connection manager that uses the real db_conn
    class MockConnectionManager:
        def get_connection(self):
            from contextlib import contextmanager
            @contextmanager
            def cm():
                yield db_conn
            return cm()

    mock_cm = MockConnectionManager()
    config = VitessConfig(host="localhost", port=3306, user="test", password="test", database="test")
    mock_client = VitessClient(config, connection_manager=mock_cm, id_resolver=None)

    repo = RevisionRepository(mock_cm, mock_client.id_resolver)

    # Insert a revision
    entity_id = "Q100000"
    revision_id = 1
    revision_data = {
        "entity": {"id": entity_id, "type": "item", "labels": {"en": {"value": "Test"}}},
        "statements": [],
        "properties": {},
        "property_counts": {},
        "labels_hashes": {},
        "descriptions_hashes": {},
        "aliases_hashes": {},
        "sitelinks_hashes": {},
    }

    # First, register the entity
    from models.infrastructure.vitess.id_resolver import IdResolver
    IdResolver.register_entity(db_conn, entity_id, mock_client)

    # Insert revision
    repo.insert(db_conn, entity_id, revision_id, revision_data)

    # Get the revision
    retrieved = repo.get_revision(12345, revision_id, mock_client)  # internal_id for Q100000

    assert retrieved is not None
    assert retrieved.entity["id"] == entity_id

    # Clean up
    repo.delete(db_conn, 12345, revision_id)
    with db_conn.cursor() as cursor:
        cursor.execute("DELETE FROM entity_id_mapping WHERE entity_id = %s", (entity_id,))
    db_conn.commit()