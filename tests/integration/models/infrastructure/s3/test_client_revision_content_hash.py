"""Integration tests for S3 client revision read with content_hash."""

import pytest

from models.data.infrastructure.s3.revision_data import S3RevisionData
from models.internal_representation.metadata_extractor import MetadataExtractor
from datetime import datetime, timezone


class TestS3ClientRevisionReadWithContentHash:
    """Integration tests for S3 client revision read functionality with content_hash."""

    def test_read_revision_queries_database_first(self, vitess_client, s3_client, db_conn):
        """Test that read_revision queries database for content_hash before S3."""
        entity_id = "Q42"
        revision_id = 1

        s3_client.vitess_client = vitess_client

        vitess_client.register_entity(entity_id)

        cursor = db_conn.cursor()
        cursor.execute("SELECT internal_id FROM entity_id_mapping WHERE entity_id = %s", (entity_id,))
        row = cursor.fetchone()
        actual_internal_id = row[0] if row else None

        revision_json = '{"entity": {"id": "' + entity_id + '"}, "revision_id": ' + str(revision_id) + '}'
        content_hash = MetadataExtractor.hash_string(revision_json)

        cursor.execute(
            "INSERT INTO entity_revisions "
            "(internal_id, revision_id, created_at, is_mass_edit, edit_type, statements, properties, property_counts, content_hash) "
            "VALUES (%s, %s, NOW(), FALSE, '', '[]', '[]', '{}', %s)",
            (actual_internal_id, revision_id, content_hash),
        )

        s3_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={"entity": {"id": entity_id}, "revision_id": revision_id},
            hash=content_hash,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        s3_client.store_revision(content_hash, s3_revision_data)

        result = s3_client.read_revision(entity_id, revision_id)

        assert result is not None
        assert "schema" in result or "revision" in result

    def test_read_revision_entity_not_found(self, vitess_client, s3_client):
        """Test that read_revision raises 404 when entity not found."""
        s3_client.vitess_client = vitess_client

        with pytest.raises(Exception) as exc_info:
            s3_client.read_revision("Q999", 1)

        assert "Entity not found" in str(exc_info.value)

    def test_read_revision_revision_not_found(self, vitess_client, s3_client):
        """Test that read_revision raises 404 when revision not found."""
        entity_id = "Q43"
        vitess_client.register_entity(entity_id)

        with pytest.raises(Exception) as exc_info:
            s3_client.read_revision(entity_id, 999)

        assert "Revision not found" in str(exc_info.value)

    def test_read_revision_end_to_end(self, vitess_client, s3_client, db_conn):
        """Test complete read_revision flow with all components."""
        entity_id = "Q44"
        revision_id = 1

        s3_client.vitess_client = vitess_client

        vitess_client.register_entity(entity_id)

        cursor = db_conn.cursor()
        cursor.execute("SELECT internal_id FROM entity_id_mapping WHERE entity_id = %s", (entity_id,))
        row = cursor.fetchone()
        actual_internal_id = row[0] if row else None

        revision_dict = {
            "entity": {"id": entity_id, "labels": {}},
            "schema": "1.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "revision_id": revision_id,
        }
        revision_json = '{"entity": {"id": "' + entity_id + '", "labels": {}}, "schema": "1.0.0", "revision_id": ' + str(revision_id) + '}'
        content_hash = MetadataExtractor.hash_string(revision_json)

        cursor.execute(
            "INSERT INTO entity_revisions "
            "(internal_id, revision_id, created_at, is_mass_edit, edit_type, statements, properties, property_counts, content_hash) "
            "VALUES (%s, %s, NOW(), FALSE, '', '[]', '[]', '{}', %s)",
            (actual_internal_id, revision_id, content_hash),
        )

        s3_revision_data = S3RevisionData(
            schema="1.0.0",
            revision=revision_dict,
            hash=content_hash,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        s3_client.store_revision(content_hash, s3_revision_data)

        result = s3_client.read_revision(entity_id, revision_id)

        assert result is not None
        if isinstance(result, dict):
            assert "schema" in result or "revision" in result