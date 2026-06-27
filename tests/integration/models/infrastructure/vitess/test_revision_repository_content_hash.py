"""Integration tests for RevisionRepository with content_hash support."""

from unittest.mock import MagicMock
from contextlib import contextmanager


class CursorContextManager:
    """Simple cursor context manager for testing."""

    def __init__(self, db_conn):
        self.db_conn = db_conn

    def __enter__(self):
        self.cursor = self.db_conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        return False


class TestRevisionRepositoryContentHash:
    """Integration tests for RevisionRepository content_hash functionality."""

    def test_create_revision_stores_content_hash(self, db_conn):
        """Test that create() stores content_hash in database."""
        from models.infrastructure.vitess.repositories.revision import (
            RevisionRepository,
        )
        from models.data.infrastructure.s3.entity_state import EntityState
        from models.data.infrastructure.s3.enums import EntityType, EditType, EditData
        from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
        from models.data.infrastructure.s3.hashes.statements_hashes import (
            StatementsHashes,
        )
        from models.infrastructure.s3.revision.revision_data import RevisionData
        from datetime import datetime, timezone

        # Setup
        # First, create entity mapping
        cursor = db_conn.cursor()
        cursor.execute("""
            INSERT INTO entity_id_mapping (entity_id, internal_id)
            VALUES ('Q1', 100)
        """)
        cursor.close()

        # Create a revision
        revision_data = RevisionData(
            schema_version="1.0",
            revision_id=1,
            entity_type=EntityType.ITEM,
            entity={},
            properties=[],
            property_counts={},
            hashes=HashMaps(statements=StatementsHashes(root=[])),
            edit=EditData(
                mass=False,
                type=EditType.MANUAL_UPDATE,
                user_id=1,
                summary="Test revision",
                at=datetime.now(timezone.utc).isoformat(),
            ),
            state=EntityState(),
            redirects_to="",
        )

        vitess_client = MagicMock()
        vitess_client.cursor = CursorContextManager(db_conn)
        vitess_client.id_resolver = MagicMock()
        vitess_client.id_resolver.resolve_id.return_value = 100

        repo = RevisionRepository(vitess_client=vitess_client)

        content_hash = 12345678901234567890
        repo.create("Q1", 1, revision_data, content_hash=content_hash)

        with CursorContextManager(db_conn) as cursor:
            cursor.execute(
                "SELECT content_hash FROM entity_revisions WHERE internal_id = 100 AND revision_id = 1"
            )
            result = cursor.fetchone()
            assert result[0] == content_hash

    def test_get_content_hash(self, db_conn):
        """Test that get_content_hash() retrieves stored hash."""
        from models.infrastructure.vitess.repositories.revision import (
            RevisionRepository,
        )

        # Setup
        # Insert entity mapping
        cursor = db_conn.cursor()
        cursor.execute("""
            INSERT INTO entity_id_mapping (entity_id, internal_id)
            VALUES ('Q2', 200)
        """)
        cursor.close()

        # Insert revision with content_hash
        revision_id = 1
        content_hash = 9876543210
        cursor = db_conn.cursor()
        cursor.execute(
            """
            INSERT INTO entity_revisions
            (internal_id, revision_id, created_at, is_mass_edit, edit_type,
             statements, properties, property_counts, user_id, edit_summary, content_hash)
            VALUES (200, 1, CURRENT_TIMESTAMP, FALSE, '', '[]', '[]', '{}', 1, 'test', %s)
        """,
            (content_hash,),
        )
        cursor.close()

        # Query content_hash
        vitess_client = MagicMock()
        vitess_client.cursor = CursorContextManager(db_conn)
        vitess_client.id_resolver = MagicMock()
        vitess_client.id_resolver.resolve_id.return_value = 200

        repo = RevisionRepository(vitess_client=vitess_client)

        result = repo.get_content_hash(200, revision_id)

        assert result == content_hash

    def test_get_content_hash_no_revision(self, db_conn):
        """Test that get_content_hash() returns 0 for non-existent revision."""
        from models.infrastructure.vitess.repositories.revision import (
            RevisionRepository,
        )

        vitess_client = MagicMock()
        vitess_client.cursor = CursorContextManager(db_conn)

        repo = RevisionRepository(vitess_client=vitess_client)

        result = repo.get_content_hash(999, 999)

        assert result == 0

    def test_create_with_cas_stores_content_hash(self, db_conn):
        """Test that create_with_cas() stores content_hash in database."""
        from models.infrastructure.vitess.repositories.revision import (
            RevisionRepository,
        )
        from models.data.infrastructure.s3.entity_state import EntityState
        from models.data.infrastructure.s3.enums import EntityType, EditType, EditData
        from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
        from models.data.infrastructure.s3.hashes.statements_hashes import (
            StatementsHashes,
        )
        from models.infrastructure.s3.revision.revision_data import RevisionData
        from datetime import datetime, timezone

        # Setup
        # Insert entity mapping and head
        cursor = db_conn.cursor()
        cursor.execute("""
            INSERT INTO entity_id_mapping (entity_id, internal_id)
            VALUES ('Q3', 300)
        """)
        cursor.execute("""
            INSERT INTO entity_head (internal_id, head_revision_id)
            VALUES (300, 0)
        """)
        cursor.close()

        # Create a revision
        revision_data = RevisionData(
            schema_version="1.0",
            revision_id=1,
            entity_type=EntityType.ITEM,
            entity={},
            properties=[],
            property_counts={},
            hashes=HashMaps(statements=StatementsHashes(root=[])),
            edit=EditData(
                mass=False,
                type=EditType.MANUAL_UPDATE,
                user_id=1,
                summary="Test CAS revision",
                at=datetime.now(timezone.utc).isoformat(),
            ),
            state=EntityState(),
            redirects_to="",
        )

        vitess_client = MagicMock()
        vitess_client.cursor = CursorContextManager(db_conn)
        vitess_client.id_resolver = MagicMock()
        vitess_client.id_resolver.resolve_id.return_value = 300

        repo = RevisionRepository(vitess_client=vitess_client)

        # Create revision with CAS and content_hash
        content_hash = 11122233344455566677
        result = repo.create_with_cas(
            "Q3", 1, revision_data, expected_revision_id=0, content_hash=content_hash
        )

        # Verify success
        assert result is True

        with CursorContextManager(db_conn) as cursor:
            cursor.execute(
                "SELECT content_hash FROM entity_revisions WHERE internal_id = 300 AND revision_id = 1"
            )
            db_result = cursor.fetchone()
            assert db_result[0] == content_hash
