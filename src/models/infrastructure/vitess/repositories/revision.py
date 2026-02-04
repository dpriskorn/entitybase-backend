"""Vitess revision repository for revision operations."""

import json
import logging
from typing import Any, cast

from pydantic import Field, validate_call

from models.common import OperationResult
from models.data.infrastructure.vitess.records.revision import (
    HistoryRevisionItemRecord,
    RevisionRecord,
)
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.infrastructure.vitess.repository import Repository
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class RevisionRepository(Repository):
    """Repository for entity revision database operations."""

    @validate_call
    def insert_revision(
        self,
        entity_id: str,
        revision_id: int,
        entity_data: RevisionData,
        content_hash: int,
        expected_revision_id: int = 0,
    ) -> None:
        """Insert a revision from RevisionData model."""
        if not expected_revision_id:
            logger.debug(f"insert_revision: calling create for {entity_id}, revision {revision_id}")
            self.create(entity_id, revision_id, entity_data, content_hash)
        else:
            logger.debug(f"insert_revision: calling create_with_cas for {entity_id}, revision {revision_id}, expected {expected_revision_id}")
            self.create_with_cas(entity_id, revision_id, entity_data, expected_revision_id, content_hash)

    @validate_call
    def get_revision(
        self, internal_entity_id: int = Field(gt=0), revision_id: int = Field(..., gt=0)
    ) -> RevisionRecord | None:
        """Get a specific revision data."""
        logger.debug(f"Getting revision {revision_id} for entity {internal_entity_id}")
        cursor = self.vitess_client.cursor
        cursor.execute(
            "SELECT statements, properties, property_counts, labels_hashes, descriptions_hashes, aliases_hashes, sitelinks_hashes FROM entity_revisions WHERE internal_id = %s AND revision_id = %s",
            (internal_entity_id, revision_id),
        )
        row = cursor.fetchone()
        if row:
            return cast(RevisionRecord, RevisionRecord.model_validate(
                {
                    "statements": json.loads(row[0]) if row[0] else [],
                    "properties": json.loads(row[1]) if row[1] else [],
                    "property_counts": json.loads(row[2]) if row[2] else {},
                    "labels_hashes": json.loads(row[3]) if row[3] else {},
                    "descriptions_hashes": json.loads(row[4]) if row[4] else [],
                    "aliases_hashes": json.loads(row[5]) if row[5] else [],
                    "sitelinks_hashes": json.loads(row[6]) if row[6] else {},
                }
            ))
        return None

    @validate_call
    def get_history(
        self, entity_id: str = Field(..., min_length=2, description="Entity ID e.g. Q1 or L1"), limit: int = Field(default=20, description="Limit number of history items"), offset: int = Field(default=0, description="Number of items to skip")
    ) -> list[Any]:
        """Get revision history for an entity."""
        logger.debug(f"Getting history for entity {entity_id}, limit {limit}")

        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            logger.debug(f"No internal ID found for entity {entity_id}")
            return []

        cursor = self.vitess_client.cursor
        cursor.execute(
                "SELECT revision_id, created_at, user_id, edit_summary FROM entity_revisions WHERE internal_id = %s ORDER BY revision_id DESC LIMIT %s OFFSET %s",
                (internal_id, limit, offset),
            )
        result = [
            HistoryRevisionItemRecord(
                revision_id=row[0],
                created_at=row[1].isoformat() if row[1] else "",
                user_id=row[2],
                edit_summary=row[3] or "",
            )
            for row in cursor.fetchall()
        ]
        logger.debug(f"Retrieved {len(result)} history items for entity {entity_id}")
        return result

    @validate_call
    def delete(self,     entity_id: str = Field(..., min_length=2, description="Entity ID e.g. Q1 or L1"),
    revision_id: int = Field(gt=0),
) -> OperationResult:
        """Delete a revision (for rollback)."""
        logger.debug(f"Deleting revision {revision_id} for entity {entity_id}")
        if not self.connection_manager.connection:
            logger.debug("Database connection not provided")
            return OperationResult(
                success=False, error="Database connection not provided"
            )
        if not entity_id:
            logger.debug("Entity ID is required")
            return OperationResult(success=False, error="Entity ID is required")
        if revision_id <= 0:
            logger.debug(f"Invalid revision ID: {revision_id}")
            return OperationResult(success=False, error="Invalid revision ID")
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            logger.debug(f"Entity {entity_id} not found for deletion")
            return OperationResult(success=False, error="Entity not found")
        cursor = self.vitess_client.cursor
        cursor.execute(
            "DELETE FROM entity_revisions WHERE internal_id = %s AND revision_id = %s",
            (internal_id, revision_id),
        )
        # Also delete from entity_head if it's the head
        cursor.execute(
            "UPDATE entity_head SET head_revision_id = head_revision_id - 1 WHERE internal_id = %s AND head_revision_id = %s",
            (internal_id, revision_id),
        )
        logger.debug(f"Successfully deleted revision {revision_id} for entity {entity_id}")
        return OperationResult(success=True)

    @validate_call
    def get_content_hash(self, internal_entity_id: int = Field(gt=0), revision_id: int = Field(..., gt=0)) -> int:
        """Get the content_hash for a specific revision."""
        cursor = self.vitess_client.cursor
        cursor.execute(
            "SELECT content_hash FROM entity_revisions WHERE internal_id = %s AND revision_id = %s",
            (internal_entity_id, revision_id),
        )
        row = cursor.fetchone()
        if row and row[0] is not None:
            return cast(int, row[0])
        raise_validation_error(f"No content_hash found for entity {internal_entity_id} revision {revision_id}", status_code=404)

    @validate_call
    def create_with_cas(
        self,
        entity_id: str,
        revision_id: int,
        entity_data: RevisionData,
        content_hash: int,
        expected_revision_id: int = 0,
    ) -> bool:
        """Create a revision with compare-and-swap semantics."""
        logger.debug(
            f"Creating revision {revision_id} for entity {entity_id} with CAS, expected {expected_revision_id}"
        )
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            logger.debug(f"Entity {entity_id} not found for CAS operation")
            return False
        statements = entity_data.hashes.statements.model_dump_json() if entity_data.hashes and entity_data.hashes.statements else "[]"

        cursor = self.vitess_client.cursor
        cursor.execute(
                """INSERT INTO entity_revisions
                        (internal_id, revision_id, is_mass_edit, edit_type, statements, properties, property_counts, created_at, user_id, edit_summary, content_hash)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    internal_id,
                    revision_id,
                    entity_data.edit.is_mass_edit,
                    entity_data.edit.edit_type,
                    statements,
                    json.dumps(entity_data.properties or []),
                    entity_data.property_counts.model_dump_json() if entity_data.property_counts else "{}",
                    entity_data.edit.at,
                    entity_data.edit.user_id,
                    entity_data.edit.edit_summary,
                    content_hash,
                ),
            )

        cursor.execute(
            """UPDATE entity_head
               SET head_revision_id = %s,
                    is_semi_protected = %s,
                    is_locked = %s,
                    is_archived = %s,
                    is_dangling = %s,
                    is_mass_edit_protected = %s
                WHERE internal_id = %s AND head_revision_id = %s""",
            (
                revision_id,
                entity_data.state.is_semi_protected,
                entity_data.state.is_locked,
                entity_data.state.is_archived,
                entity_data.state.is_dangling,
                entity_data.state.is_mass_edit_protected,
                internal_id,
                expected_revision_id,
            ),
        )

        affected_rows = int(cursor.rowcount)
        logger.debug(f"CAS operation: affected {affected_rows} rows for revision {revision_id}")
        return affected_rows > 0

    def create(self, entity_id: str, revision_id: int, entity_data: RevisionData, content_hash: int) -> None:
        """Create a new revision for an entity."""
        logger.debug(f"Creating revision {revision_id} for entity {entity_id}")
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            raise_validation_error(f"Entity {entity_id} not found", status_code=404)
        statements = entity_data.hashes.statements.model_dump_json() if entity_data.hashes and entity_data.hashes.statements else "[]"

        # Check if revision already exists to make insert idempotent
        cursor = self.vitess_client.cursor
        cursor.execute(
            "SELECT COUNT(*) FROM entity_revisions WHERE internal_id = %s AND revision_id = %s",
            (internal_id, revision_id)
        )
        if cursor.fetchone()[0] > 0:
            logger.debug(f"Revision {revision_id} for entity {entity_id} already exists, skipping")
            return

        cursor.execute(
            """INSERT INTO entity_revisions
                    (internal_id, revision_id, is_mass_edit, edit_type, statements, properties, property_counts, created_at, user_id, edit_summary, content_hash)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                internal_id,
                revision_id,
                entity_data.edit.is_mass_edit,
                entity_data.edit.edit_type,
                statements,
                json.dumps(entity_data.properties or []),
                entity_data.property_counts.model_dump_json() if entity_data.property_counts else "{}",
                entity_data.edit.at,
                entity_data.edit.user_id,
                entity_data.edit.edit_summary,
                content_hash,
            ),
        )

        cursor.execute(
            """INSERT INTO entity_head
                   (internal_id, head_revision_id, is_semi_protected, is_locked, is_archived, is_dangling, is_mass_edit_protected, is_deleted, is_redirect)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE
                      head_revision_id = VALUES(head_revision_id),
                      is_semi_protected = VALUES(is_semi_protected),
                      is_locked = VALUES(is_locked),
                      is_archived = VALUES(is_archived),
                      is_dangling = VALUES(is_dangling),
                      is_mass_edit_protected = VALUES(is_mass_edit_protected),
                      is_deleted = VALUES(is_deleted),
                      is_redirect = VALUES(is_redirect)""",
            (
                internal_id,
                revision_id,
                entity_data.state.is_semi_protected,
                entity_data.state.is_locked,
                entity_data.state.is_archived,
                entity_data.state.is_dangling,
                entity_data.state.is_mass_edit_protected,
                False,
                False,
            ),
        )
        logger.debug(f"Successfully created revision {revision_id} for entity {entity_id}")
